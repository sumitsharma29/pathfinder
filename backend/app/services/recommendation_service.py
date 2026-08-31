import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Tuple
from collections import defaultdict
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.exceptions import NotFoundError, AuthorizationError
from backend.app.models.learner_profile import LearnerProfile
from backend.app.models.resource import Resource
from backend.app.models.project import Project
from backend.app.models.recommendation import Recommendation
from backend.app.models.feedback import Feedback
from backend.app.repositories.learner_profile_repository import LearnerProfileRepository
from backend.app.repositories.skill_repository import SkillRepository
from backend.app.repositories.role_repository import RoleRepository
from backend.app.repositories.resource_repository import ResourceRepository
from backend.app.repositories.project_repository import ProjectRepository
from backend.app.repositories.recommendation_repository import RecommendationRepository
from backend.app.services.skill_gap_service import SkillGapService
from backend.app.schemas.recommendation import (
    RecommendationItem, RecommendationReason, ResourceSummary,
    ProjectSummary, FeedbackCreateRequest, FeedbackResponse
)


class RecommendationService:
    """Deterministic, Explainable, Server-side Recommendation Engine."""

    @classmethod
    def get_recommendations(
        cls,
        db: Session,
        user_id: uuid.UUID,
        skill_id: Optional[uuid.UUID] = None,
        resource_type: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
        page_size: int = 20
    ) -> List[RecommendationItem]:
        """Compute and return personalized recommendations for authenticated learner."""
        # 1. Fetch learner profile
        profile = LearnerProfileRepository.get_by_user_id(db, user_id)
        if not profile:
            raise NotFoundError(message="Learner profile not found")

        if not profile.target_role_id:
            raise NotFoundError(
                message="No target career role selected. Please set a target role in your profile to receive recommendations."
            )

        # 2. Compute dynamic skill gaps
        gap_analysis = SkillGapService.analyze_gaps(db, user_id=user_id)
        gaps_by_skill_id = {item.skill_id: item for item in gap_analysis.skills}
        role_skills = RoleRepository.get_role_skills(db, profile.target_role_id)
        role_skill_importance = {rs.skill_id: float(rs.importance) for rs in role_skills}

        # 3. Retrieve learner's current skills
        learner_skills = LearnerProfileRepository.get_learner_skills(db, profile.id)
        learner_proficiency = {ls.skill_id: float(ls.proficiency) for ls in learner_skills}

        # 4. Retrieve prerequisite graph
        all_prereqs = SkillRepository.get_all_prerequisites(db)
        prereqs_by_skill: Dict[uuid.UUID, List[uuid.UUID]] = defaultdict(list)
        for p in all_prereqs:
            prereqs_by_skill[p.skill_id].append(p.prerequisite_skill_id)

        # 5. Fetch feedback to downweight negative feedback
        feedback_list = RecommendationRepository.get_feedback_for_learner(db, profile.id)
        not_helpful_resources = {
            fb.resource_id for fb in feedback_list if fb.feedback_type == "not_helpful"
        }

        # 6. Retrieve candidate resources and projects
        candidates_scored: List[Tuple[float, float, str, Optional[Resource], Optional[Project], Optional[uuid.UUID], RecommendationReason]] = []

        # Resources candidates
        active_resources = ResourceRepository.get_all(db, skill_id=skill_id, resource_type=resource_type)
        daily_hours = float(profile.daily_study_hours) if profile.daily_study_hours is not None else 2.0
        preferences = profile.learning_preferences or {}
        favored_content_types = preferences.get("content_types", [])

        for res in active_resources:
            # Skip if explicitly flagged as not helpful
            if res.id in not_helpful_resources:
                continue

            # Identify covered skills
            covered_skill_ids = [rs.skill_id for rs in res.resource_skills]
            if not covered_skill_ids:
                continue

            # Find primary skill with maximum gap relevance
            best_skill_id = None
            max_gap = -1.0
            primary_importance = 0.5
            primary_skill_name = "General"

            for s_id in covered_skill_ids:
                if s_id in gaps_by_skill_id:
                    gap_item = gaps_by_skill_id[s_id]
                    if gap_item.gap > max_gap:
                        max_gap = gap_item.gap
                        best_skill_id = s_id
                        primary_importance = gap_item.importance
                        primary_skill_name = gap_item.skill
                elif best_skill_id is None:
                    best_skill_id = s_id
                    if res.resource_skills:
                        primary_skill_name = res.resource_skills[0].skill.name if res.resource_skills[0].skill else "Skill"

            primary_skill_id = best_skill_id or covered_skill_ids[0]

            # Calculate Component Scores:
            # A. Skill Gap Relevance (0.0 to 1.0)
            if max_gap >= 0:
                s_gap = min(max_gap / 100.0, 1.0)
            else:
                s_gap = 0.1

            # B. Prerequisite Fit (0.0 to 1.0)
            direct_prereqs = prereqs_by_skill.get(primary_skill_id, [])
            if not direct_prereqs:
                s_prereq = 1.0
            else:
                prereq_scores = []
                for p_id in direct_prereqs:
                    p_prof = learner_proficiency.get(p_id, 0.0)
                    if p_prof == 0.0:
                        prereq_scores.append(0.1)  # Missing prerequisite penalty
                    else:
                        prereq_scores.append(min(p_prof / 70.0, 1.0))
                s_prereq = sum(prereq_scores) / len(prereq_scores)

            # C. Goal Relevance (0.0 to 1.0)
            if primary_skill_id in role_skill_importance:
                s_goal = role_skill_importance[primary_skill_id]
            else:
                s_goal = 0.2

            # D. Difficulty Fit (0.0 to 1.0)
            curr_prof = learner_proficiency.get(primary_skill_id, 0.0)
            res_diff = (res.difficulty or "intermediate").lower()
            if curr_prof < 35:  # Beginner stage
                s_diff = 1.0 if res_diff == "beginner" else (0.6 if res_diff == "intermediate" else 0.2)
            elif curr_prof < 70:  # Intermediate stage
                s_diff = 1.0 if res_diff == "intermediate" else (0.7 if res_diff == "beginner" else 0.7)
            else:  # Advanced stage
                s_diff = 1.0 if res_diff == "advanced" else (0.7 if res_diff == "intermediate" else 0.3)

            # E. Time Fit (0.0 to 1.0)
            est_hours = float(res.estimated_minutes) / 60.0 if res.estimated_minutes is not None else 5.0
            weekly_capacity = max(daily_hours * 7.0, 5.0)
            if est_hours <= weekly_capacity:
                s_time = 1.0
            else:
                s_time = max(0.3, round(1.0 - (est_hours - weekly_capacity) / 100.0, 2))

            # F. Preference Fit (0.0 to 1.0)
            res_type = (res.resource_type or "").lower()
            if favored_content_types:
                s_pref = 1.0 if res_type in [t.lower() for t in favored_content_types] else 0.5
            else:
                s_pref = 0.8

            # Calculate Final Weighted Score
            final_score = round(
                settings.SKILL_GAP_WEIGHT * s_gap
                + settings.PREREQUISITE_WEIGHT * s_prereq
                + settings.GOAL_WEIGHT * s_goal
                + settings.DIFFICULTY_WEIGHT * s_diff
                + settings.TIME_WEIGHT * s_time
                + settings.PREFERENCE_WEIGHT * s_pref,
                4
            )

            # Generate Explainability Reason
            reason_text = (
                f"Recommended because {primary_skill_name} is a target skill gap (gap: {max(max_gap, 0.0):.1f}), "
                f"prerequisite readiness is {s_prereq * 100:.0f}%, and the {res_diff} difficulty matches your current level."
            )

            reason_obj = RecommendationReason(
                skill_gap=round(s_gap, 4),
                prerequisite_fit=round(s_prereq, 4),
                goal_relevance=round(s_goal, 4),
                difficulty_fit=round(s_diff, 4),
                time_fit=round(s_time, 4),
                preference_fit=round(s_pref, 4),
                explanation=reason_text,
                primary_skill=primary_skill_name
            )

            quality_score = float(res.quality_score) if res.quality_score is not None else 0.8
            candidates_scored.append(
                (final_score, quality_score, str(res.id), res, None, primary_skill_id, reason_obj)
            )

        # 7. Project Candidates (if resource_type is not restricting to courses/videos only)
        if not resource_type or resource_type.lower() == "project":
            all_projects = ProjectRepository.get_all(db, skill_id=skill_id)
            for proj in all_projects:
                covered_skill_ids = [ps.skill_id for ps in proj.project_skills]
                if not covered_skill_ids:
                    continue

                best_skill_id = None
                max_gap = -1.0
                primary_skill_name = "Project Skill"

                for s_id in covered_skill_ids:
                    if s_id in gaps_by_skill_id:
                        gap_item = gaps_by_skill_id[s_id]
                        if gap_item.gap > max_gap:
                            max_gap = gap_item.gap
                            best_skill_id = s_id
                            primary_skill_name = gap_item.skill

                primary_skill_id = best_skill_id or covered_skill_ids[0]
                s_gap = min(max_gap / 100.0, 1.0) if max_gap >= 0 else 0.2

                # Prerequisite fit
                direct_prereqs = prereqs_by_skill.get(primary_skill_id, [])
                if not direct_prereqs:
                    s_prereq = 1.0
                else:
                    prereq_scores = [min(learner_proficiency.get(p, 0.0) / 70.0, 1.0) for p in direct_prereqs]
                    s_prereq = sum(prereq_scores) / len(prereq_scores) if prereq_scores else 1.0

                s_goal = role_skill_importance.get(primary_skill_id, 0.3)
                curr_prof = learner_proficiency.get(primary_skill_id, 0.0)
                p_diff = (proj.difficulty or "intermediate").lower()
                s_diff = 1.0 if (curr_prof >= 40 and p_diff in ["intermediate", "advanced"]) else 0.7
                s_time = 0.8
                s_pref = 1.0 if "project" in [t.lower() for t in favored_content_types] else 0.8

                final_score = round(
                    settings.SKILL_GAP_WEIGHT * s_gap
                    + settings.PREREQUISITE_WEIGHT * s_prereq
                    + settings.GOAL_WEIGHT * s_goal
                    + settings.DIFFICULTY_WEIGHT * s_diff
                    + settings.TIME_WEIGHT * s_time
                    + settings.PREFERENCE_WEIGHT * s_pref,
                    4
                )

                reason_text = (
                    f"Practical project applying {primary_skill_name} to reinforce hands-on proficiency and mastery."
                )

                reason_obj = RecommendationReason(
                    skill_gap=round(s_gap, 4),
                    prerequisite_fit=round(s_prereq, 4),
                    goal_relevance=round(s_goal, 4),
                    difficulty_fit=round(s_diff, 4),
                    time_fit=round(s_time, 4),
                    preference_fit=round(s_pref, 4),
                    explanation=reason_text,
                    primary_skill=primary_skill_name
                )

                candidates_scored.append(
                    (final_score, 0.9, str(proj.id), None, proj, primary_skill_id, reason_obj)
                )

        # 8. Sort candidates deterministically: final_score DESC, quality_score DESC, candidate_id ASC
        candidates_scored.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)

        # 9. Clean refresh & persist top recommendations for this learner
        RecommendationRepository.clear_previous_recommendations(db, profile.id)

        recommendations_result: List[RecommendationItem] = []
        seen_ids = set()

        for rank, (score, quality, cand_id, res_obj, proj_obj, primary_skill_id, reason_obj) in enumerate(candidates_scored[:limit], start=1):
            if cand_id in seen_ids:
                continue
            seen_ids.add(cand_id)

            persisted_rec = RecommendationRepository.create(
                db=db,
                learner_id=profile.id,
                skill_id=primary_skill_id,
                resource_id=res_obj.id if res_obj else None,
                score=score,
                ranking=rank,
                reason=reason_obj.model_dump(),
                algorithm_version="v1"
            )

            res_summary = None
            if res_obj:
                skills_covered = [rs.skill.name for rs in res_obj.resource_skills if rs.skill]
                res_summary = ResourceSummary(
                    id=res_obj.id,
                    title=res_obj.title,
                    url=res_obj.url,
                    resource_type=res_obj.resource_type,
                    provider=res_obj.provider,
                    difficulty=res_obj.difficulty,
                    estimated_hours=round(float(res_obj.estimated_minutes) / 60.0, 2) if res_obj.estimated_minutes is not None else None,
                    quality_score=float(res_obj.quality_score) if res_obj.quality_score is not None else None,
                    is_free=bool(res_obj.meta_data.get("is_free", True)) if isinstance(res_obj.meta_data, dict) else True,
                    skills_covered=skills_covered
                )

            proj_summary = None
            if proj_obj:
                skills_covered = [ps.skill.name for ps in proj_obj.project_skills if ps.skill]
                proj_summary = ProjectSummary(
                    id=proj_obj.id,
                    title=proj_obj.title,
                    description=proj_obj.description,
                    difficulty=proj_obj.difficulty,
                    estimated_hours=float(proj_obj.estimated_hours) if proj_obj.estimated_hours is not None else None,
                    skills_covered=skills_covered
                )

            recommendations_result.append(
                RecommendationItem(
                    id=persisted_rec.id,
                    item_type="resource" if res_obj else "project",
                    resource=res_summary,
                    project=proj_summary,
                    skill_id=primary_skill_id,
                    skill_name=reason_obj.primary_skill,
                    score=score,
                    ranking=rank,
                    reason=reason_obj,
                    algorithm_version="v1",
                    created_at=persisted_rec.created_at
                )
            )

        db.commit()
        return recommendations_result

    @classmethod
    def get_recommendation_by_id(
        cls,
        db: Session,
        user_id: uuid.UUID,
        recommendation_id: uuid.UUID
    ) -> RecommendationItem:
        """Retrieve a specific recommendation by ID, enforcing user ownership."""
        profile = LearnerProfileRepository.get_by_user_id(db, user_id)
        if not profile:
            raise NotFoundError(message="Learner profile not found")

        rec = RecommendationRepository.get_by_id(db, recommendation_id)
        if not rec:
            raise NotFoundError(message="Recommendation not found")

        if rec.learner_id != profile.id:
            raise AuthorizationError(message="Access forbidden to this recommendation")

        reason_data = rec.reason if isinstance(rec.reason, dict) else {}
        reason_obj = RecommendationReason(
            skill_gap=reason_data.get("skill_gap", 0.0),
            prerequisite_fit=reason_data.get("prerequisite_fit", 1.0),
            goal_relevance=reason_data.get("goal_relevance", 1.0),
            difficulty_fit=reason_data.get("difficulty_fit", 1.0),
            time_fit=reason_data.get("time_fit", 1.0),
            preference_fit=reason_data.get("preference_fit", 1.0),
            explanation=reason_data.get("explanation", "Recommended based on your learning profile"),
            primary_skill=reason_data.get("primary_skill")
        )

        res_summary = None
        if rec.resource:
            res_summary = ResourceSummary(
                id=rec.resource.id,
                title=rec.resource.title,
                url=rec.resource.url,
                resource_type=rec.resource.resource_type,
                provider=rec.resource.provider,
                difficulty=rec.resource.difficulty,
                estimated_hours=round(float(rec.resource.estimated_minutes) / 60.0, 2) if rec.resource.estimated_minutes is not None else None,
                quality_score=float(rec.resource.quality_score) if rec.resource.quality_score is not None else None,
                is_free=bool(rec.resource.meta_data.get("is_free", True)) if isinstance(rec.resource.meta_data, dict) else True,
                skills_covered=[rs.skill.name for rs in rec.resource.resource_skills if rs.skill]
            )

        return RecommendationItem(
            id=rec.id,
            item_type="resource" if rec.resource_id else "project",
            resource=res_summary,
            project=None,
            skill_id=rec.skill_id,
            skill_name=rec.skill.name if rec.skill else None,
            score=float(rec.score),
            ranking=rec.ranking,
            reason=reason_obj,
            algorithm_version=rec.algorithm_version or "v1",
            created_at=rec.created_at
        )

    @classmethod
    def submit_feedback(
        cls,
        db: Session,
        user_id: uuid.UUID,
        recommendation_id: uuid.UUID,
        feedback_in: FeedbackCreateRequest
    ) -> FeedbackResponse:
        """Submit feedback on a recommendation."""
        profile = LearnerProfileRepository.get_by_user_id(db, user_id)
        if not profile:
            raise NotFoundError(message="Learner profile not found")

        rec = RecommendationRepository.get_by_id(db, recommendation_id)
        if not rec:
            raise NotFoundError(message="Recommendation not found")

        if rec.learner_id != profile.id:
            raise AuthorizationError(message="Access forbidden to this recommendation")

        fb = RecommendationRepository.create_feedback(
            db=db,
            learner_id=profile.id,
            resource_id=rec.resource_id,
            feedback_type=feedback_in.feedback_type,
            rating=feedback_in.rating,
            comment=feedback_in.comment
        )
        db.commit()
        db.refresh(fb)

        return FeedbackResponse(
            id=fb.id,
            learner_id=fb.learner_id,
            resource_id=fb.resource_id,
            feedback_type=fb.feedback_type,
            rating=fb.rating,
            comment=fb.comment,
            created_at=fb.created_at
        )
