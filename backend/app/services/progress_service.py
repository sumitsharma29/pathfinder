import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload, joinedload

from backend.app.models.user import User
from backend.app.models.learner_profile import LearnerProfile
from backend.app.models.learner_skill import LearnerSkill
from backend.app.models.roadmap import Roadmap
from backend.app.models.roadmap_item import RoadmapItem
from backend.app.models.progress import Progress
from backend.app.models.assessment_result import AssessmentResult
from backend.app.models.role import Role
from backend.app.models.role_skill import RoleSkill
from backend.app.models.skill import Skill
from backend.app.core.exceptions import NotFoundError
from backend.app.services.skill_gap_service import SkillGapService
from backend.app.services.recommendation_service import RecommendationService
from backend.app.services.adaptive_learning_service import AdaptiveLearningService
from backend.app.schemas.progress import (
    OverallProgressResponse,
    SkillProgressItem,
    MilestoneProgressItem,
    MilestoneSummary,
    DashboardOverview,
    DashboardCompletedMetrics,
    DashboardWeakAreas,
    DashboardLearningFocus,
    DashboardAggregationResponse,
)


class ProgressService:
    """Service handling learner progress calculation, skill growth tracking,

    milestone metrics, and unified dashboard aggregation.
    """

    @staticmethod
    def _item_title(item: RoadmapItem) -> str:
        if item.skill:
            return item.skill.name
        if item.resource:
            return item.resource.title
        if item.project:
            return item.project.title
        return f"Milestone {item.sequence}"

    @staticmethod
    def _item_minutes(item: RoadmapItem) -> int:
        if item.estimated_hours:
            return int(float(item.estimated_hours) * 60)
        if item.resource and item.resource.estimated_minutes:
            return item.resource.estimated_minutes
        if item.project and item.project.estimated_hours:
            return int(float(item.project.estimated_hours) * 60)
        return 60

    @classmethod
    def get_overall_progress(cls, db: Session, user_id: uuid.UUID) -> OverallProgressResponse:
        """Calculate overall learner progress strictly from actual database state."""
        profile = db.execute(
            select(LearnerProfile).where(LearnerProfile.user_id == user_id)
        ).scalar_one_or_none()

        if not profile:
            raise NotFoundError("Learner profile not found")

        # Fetch active roadmap with items
        active_roadmap = db.execute(
            select(Roadmap)
            .options(
                selectinload(Roadmap.items).joinedload(RoadmapItem.skill),
                selectinload(Roadmap.items).joinedload(RoadmapItem.resource),
                selectinload(Roadmap.items).joinedload(RoadmapItem.project)
            )
            .where(Roadmap.learner_id == profile.id, Roadmap.status == "active")
        ).scalar_one_or_none()

        if not active_roadmap or not active_roadmap.items:
            return OverallProgressResponse(
                overall_percentage=0.0,
                completed_items=0,
                total_items=0,
                time_spent_minutes=0,
                active_roadmap_id=active_roadmap.id if active_roadmap else None,
                current_milestone=None
            )

        items = active_roadmap.items
        total_items = len(items)
        completed_items = sum(1 for it in items if it.status == "COMPLETED")
        overall_percentage = round((completed_items / total_items) * 100.0, 2) if total_items > 0 else 0.0

        # Calculate time spent strictly from actual Progress records
        progress_records = db.execute(
            select(Progress).where(Progress.learner_id == profile.id)
        ).scalars().all()

        total_time_spent = sum(p.time_spent_minutes for p in progress_records if p.time_spent_minutes)

        # Identify current milestone (IN_PROGRESS first, then earliest AVAILABLE)
        in_progress_item = next((it for it in sorted(items, key=lambda x: x.sequence) if it.status == "IN_PROGRESS"), None)
        available_item = next((it for it in sorted(items, key=lambda x: x.sequence) if it.status == "AVAILABLE"), None)
        active_milestone = in_progress_item or available_item

        current_milestone_summary = None
        if active_milestone:
            current_milestone_summary = MilestoneSummary(
                roadmap_item_id=active_milestone.id,
                title=cls._item_title(active_milestone),
                status=active_milestone.status,
                sequence_order=active_milestone.sequence,
                estimated_minutes=cls._item_minutes(active_milestone),
                skill_id=active_milestone.skill_id or active_milestone.id,
                skill_name=active_milestone.skill.name if active_milestone.skill else cls._item_title(active_milestone)
            )

        return OverallProgressResponse(
            overall_percentage=overall_percentage,
            completed_items=completed_items,
            total_items=total_items,
            time_spent_minutes=total_time_spent,
            active_roadmap_id=active_roadmap.id,
            current_milestone=current_milestone_summary
        )

    @classmethod
    def get_skill_progress(cls, db: Session, user_id: uuid.UUID) -> List[SkillProgressItem]:
        """Return skill-level progress across all skills required for the learner's target role."""
        profile = db.execute(
            select(LearnerProfile).where(LearnerProfile.user_id == user_id)
        ).scalar_one_or_none()

        if not profile or not profile.target_role_id:
            return []

        # Use deterministic SkillGapService to evaluate current skill state
        skill_gaps_data = SkillGapService.analyze_gaps(
            db=db,
            user_id=user_id
        )

        return [
            SkillProgressItem(
                skill_id=item.skill_id,
                skill=item.skill,
                category=item.category,
                current_proficiency=item.current,
                required_proficiency=item.required,
                gap=item.gap,
                status=item.status,
                importance=item.importance
            )
            for item in skill_gaps_data.skills
        ]

    @classmethod
    def get_milestone_progress(cls, db: Session, user_id: uuid.UUID) -> List[MilestoneProgressItem]:
        """Return milestone-level breakdown for the active roadmap."""
        profile = db.execute(
            select(LearnerProfile).where(LearnerProfile.user_id == user_id)
        ).scalar_one_or_none()

        if not profile:
            raise NotFoundError("Learner profile not found")

        active_roadmap = db.execute(
            select(Roadmap)
            .options(
                selectinload(Roadmap.items).joinedload(RoadmapItem.skill),
                selectinload(Roadmap.items).joinedload(RoadmapItem.resource),
                selectinload(Roadmap.items).joinedload(RoadmapItem.project)
            )
            .where(Roadmap.learner_id == profile.id, Roadmap.status == "active")
        ).scalar_one_or_none()

        if not active_roadmap or not active_roadmap.items:
            return []

        sorted_items = sorted(active_roadmap.items, key=lambda x: x.sequence)

        result = []
        for it in sorted_items:
            pct = 100.0 if it.status == "COMPLETED" else 0.0
            result.append(
                MilestoneProgressItem(
                    roadmap_item_id=it.id,
                    title=cls._item_title(it),
                    status=it.status,
                    percentage=pct,
                    sequence_order=it.sequence,
                    estimated_minutes=cls._item_minutes(it),
                    skill_id=it.skill_id or it.id,
                    skill_name=it.skill.name if it.skill else cls._item_title(it),
                    resource_id=it.resource_id,
                    resource_title=it.resource.title if it.resource else None
                )
            )
        return result

    @classmethod
    def get_dashboard_data(cls, db: Session, user_id: uuid.UUID) -> DashboardAggregationResponse:
        """Aggregate the 5 essential dashboard answers for the learner:

        1. Where am I?
        2. What have I completed?
        3. What am I weak at?
        4. What am I learning?
        5. What should I do next?
        """
        profile = db.execute(
            select(LearnerProfile)
            .options(joinedload(LearnerProfile.target_role))
            .where(LearnerProfile.user_id == user_id)
        ).scalar_one_or_none()

        if not profile:
            raise NotFoundError("Learner profile not found")

        # 1. Overall Progress & Roadmap
        overall_progress = cls.get_overall_progress(db, user_id)

        active_roadmap = None
        roadmap_version = 1
        if overall_progress.active_roadmap_id:
            active_roadmap = db.execute(
                select(Roadmap).where(Roadmap.id == overall_progress.active_roadmap_id)
            ).scalar_one_or_none()
            if active_roadmap:
                roadmap_version = active_roadmap.version

        # Skill gaps & readiness
        readiness_score = 0.0
        total_skills_count = 0
        mastered_skills_count = 0
        critical_skill_gaps = 0

        if profile.target_role_id:
            gap_data = SkillGapService.analyze_gaps(
                db=db,
                user_id=user_id
            )
            readiness_score = gap_data.summary.overall_readiness_percentage
            total_skills_count = gap_data.summary.total_skills_required
            mastered_skills_count = gap_data.summary.skills_mastered
            critical_skill_gaps = sum(1 for g in gap_data.skills if g.status in ["MISSING", "PARTIAL"] and g.importance >= 0.8)

        # 2. Completed Metrics
        completed_assessments_count = db.execute(
            select(func.count(AssessmentResult.id)).where(AssessmentResult.learner_id == profile.id)
        ).scalar() or 0

        completed_metrics = DashboardCompletedMetrics(
            completed_milestones_count=overall_progress.completed_items,
            mastered_skills_count=mastered_skills_count,
            total_skills_count=total_skills_count,
            completed_assessments_count=completed_assessments_count,
            total_time_spent_minutes=overall_progress.time_spent_minutes
        )

        # 3. Weak Areas & Interventions
        weak_skills_data = AdaptiveLearningService.detect_weak_skills(db, profile.id, profile.target_role_id)
        interventions = AdaptiveLearningService.select_interventions(db, weak_skills_data, profile.id)

        weak_areas = DashboardWeakAreas(
            weak_skills=[w["skill_name"] for w in weak_skills_data],
            critical_skill_gaps=critical_skill_gaps,
            interventions_needed=interventions
        )

        # 4. Learning Focus (Active Milestone & Recommendations)
        active_recommendations = []
        if profile.target_role_id:
            try:
                active_recommendations = RecommendationService.get_recommendations(
                    db=db,
                    user_id=user_id,
                    limit=3
                )
            except Exception:
                pass

        learning_focus = DashboardLearningFocus(
            current_milestone=overall_progress.current_milestone,
            active_recommendations=active_recommendations
        )

        # 5. Next Best Action
        next_action = AdaptiveLearningService.get_next_best_action(db, user_id)

        overview = DashboardOverview(
            target_role_id=profile.target_role_id,
            target_role_title=profile.target_role.name if profile.target_role else None,
            readiness_score=readiness_score,
            overall_progress_percentage=overall_progress.overall_percentage,
            active_roadmap_id=overall_progress.active_roadmap_id,
            roadmap_version=roadmap_version
        )

        return DashboardAggregationResponse(
            overview=overview,
            completed_metrics=completed_metrics,
            weak_areas=weak_areas,
            learning_focus=learning_focus,
            next_best_action=next_action
        )
