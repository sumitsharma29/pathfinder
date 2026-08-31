import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.config import settings
from backend.app.core.exceptions import NotFoundError, AppException
from backend.app.models.learner_profile import LearnerProfile
from backend.app.models.skill import Skill
from backend.app.models.role import Role
from backend.app.models.role_skill import RoleSkill
from backend.app.models.skill_prerequisite import SkillPrerequisite
from backend.app.models.roadmap import Roadmap
from backend.app.models.roadmap_item import RoadmapItem
from backend.app.models.resource import Resource
from backend.app.models.assessment import Assessment

from backend.app.repositories.learner_profile_repository import LearnerProfileRepository
from backend.app.repositories.skill_repository import SkillRepository
from backend.app.repositories.role_repository import RoleRepository
from backend.app.repositories.roadmap_repository import RoadmapRepository
from backend.app.repositories.resource_repository import ResourceRepository
from backend.app.repositories.assessment_repository import AssessmentRepository

from backend.app.services.skill_gap_service import SkillGapService
from backend.app.services.roadmap_service import RoadmapService
from backend.app.services.recommendation_service import RecommendationService

from backend.app.schemas.adaptive import (
    AdaptiveIntervention, NextBestActionResponse, AdaptiveEvaluationResponse
)
from backend.app.schemas.recommendation import ResourceSummary


class AdaptiveLearningService:
    """Deterministic Adaptive Learning Engine for PathFinder AI.

    Continuously monitors learner state changes (assessment mastery, role changes,
    skill proficiency updates, roadmap milestones) and dynamically adapts the learner's
    roadmap, interventions, recommendations, and next best action based on real evidence.
    """

    # Configurable Mastery Thresholds (AI_SPEC.md §31, TECHNICAL.md §50)
    MASTERY_MASTERED: float = settings.MASTERY_MASTERED
    MASTERY_CONTINUE: float = settings.MASTERY_CONTINUE
    MASTERY_REINFORCEMENT: float = settings.MASTERY_REINFORCEMENT

    @classmethod
    def evaluate_and_adapt(
        cls,
        db: Session,
        user_id: uuid.UUID,
        trigger_event: str = "MANUAL_EVALUATION",
        context: Optional[Dict[str, Any]] = None
    ) -> AdaptiveEvaluationResponse:
        """Evaluate learner state changes, re-evaluate dependencies, adapt roadmap and recommendations,

        and compute the deterministic next best action.
        """
        context = context or {}

        # Pessimistic row locking on learner profile for concurrency safety
        profile = (
            db.query(LearnerProfile)
            .filter(LearnerProfile.user_id == user_id)
            .with_for_update()
            .first()
        )
        if not profile:
            raise NotFoundError(message="Learner profile not found")

        # 1. Detect Weak Skills
        weak_skills = cls.detect_weak_skills(db, profile.id, profile.target_role_id)

        # 2. Select Adaptive Interventions
        interventions = cls.select_interventions(db, weak_skills, profile.id)

        # 3. Check / Adapt Roadmap State
        roadmap = RoadmapRepository.get_active_roadmap(db, profile.id)
        roadmap_updated = False
        unlocked_count = 0
        locked_count = 0
        state_changes_summary: List[str] = []

        # Handle Role Change Adaptation
        if trigger_event == "ROLE_CHANGE" or (
            roadmap and profile.target_role_id and roadmap.target_role_id != profile.target_role_id
        ):
            # Target role has changed -> regenerate roadmap for the new role
            if profile.target_role_id:
                new_roadmap_resp = RoadmapService.generate_roadmap(
                    db=db,
                    user_id=user_id
                )
                roadmap = RoadmapRepository.get_by_id(db, new_roadmap_resp.id)
                roadmap_updated = True
                state_changes_summary.append(
                    f"Target role changed to '{new_roadmap_resp.target_role_name}'. New roadmap v{new_roadmap_resp.version} generated."
                )
        elif roadmap:
            # Re-evaluate prerequisite eligibility on the active roadmap
            unlocked_count, locked_count, status_changes = cls.adapt_roadmap_prerequisites(
                db=db,
                learner_id=profile.id,
                roadmap=roadmap
            )
            if status_changes:
                roadmap_updated = True
                state_changes_summary.extend(status_changes)

        # 4. Determine Next Best Action
        next_action = cls.get_next_best_action(db, user_id, active_interventions=interventions)

        # 5. Formulate Explainable Reason
        if state_changes_summary:
            reason = " | ".join(state_changes_summary)
        elif trigger_event == "ASSESSMENT":
            skill_name = context.get("skill_name", "Skill")
            score = context.get("score", 0.0)
            mastery = context.get("mastery", 0.0)
            reason = f"Assessment for {skill_name} completed with score {score:.1f}% (Mastery: {mastery:.1f}%). Learning path is up to date."
        elif interventions:
            reason = f"Identified {len(interventions)} intervention(s) to reinforce foundational understanding."
        else:
            reason = "Learning path evaluated against current skill mastery and prerequisite dependencies. No structural roadmap changes required."

        db.commit()

        return AdaptiveEvaluationResponse(
            learner_id=profile.id,
            trigger_event=trigger_event,
            state_changed=roadmap_updated or len(interventions) > 0,
            weak_skills_detected=weak_skills,
            interventions=interventions,
            roadmap_updated=roadmap_updated,
            roadmap_id=roadmap.id if roadmap else None,
            roadmap_version=roadmap.version if roadmap else None,
            unlocked_items_count=unlocked_count,
            locked_items_count=locked_count,
            next_best_action=next_action,
            reason=reason,
            evaluated_at=datetime.now(timezone.utc)
        )

    @classmethod
    def detect_weak_skills(
        cls,
        db: Session,
        learner_id: uuid.UUID,
        target_role_id: Optional[uuid.UUID] = None
    ) -> List[Dict[str, Any]]:
        """Identify weak skills (< 60% proficiency or substantial skill gap in target role)."""
        learner_skills = LearnerProfileRepository.get_learner_skills(db, learner_id)
        current_profs = {ls.skill_id: float(ls.proficiency) for ls in learner_skills}

        weak_skills: List[Dict[str, Any]] = []

        if target_role_id:
            role_skills = RoleRepository.get_role_skills(db, target_role_id)
            for rs in role_skills:
                curr_prof = current_profs.get(rs.skill_id, 0.0)
                req_prof = float(rs.required_proficiency)
                gap = max(0.0, req_prof - curr_prof)

                # Classify mastery levels according to AI_SPEC.md §31
                if curr_prof < cls.MASTERY_REINFORCEMENT:
                    category = "FOUNDATIONAL_INTERVENTION"
                    severity = "critical"
                elif curr_prof < cls.MASTERY_CONTINUE:
                    category = "TARGETED_REINFORCEMENT"
                    severity = "moderate"
                elif curr_prof < req_prof:
                    category = "CONTINUE"
                    severity = "minor"
                else:
                    category = "MASTERED"
                    severity = "none"

                if severity in ["critical", "moderate"]:
                    weak_skills.append({
                        "skill_id": rs.skill_id,
                        "skill_name": rs.skill.name if rs.skill else "Unknown",
                        "skill_slug": rs.skill.slug if rs.skill else "",
                        "current_proficiency": curr_prof,
                        "required_proficiency": req_prof,
                        "gap": round(gap, 2),
                        "importance": float(rs.importance),
                        "category": category,
                        "severity": severity
                    })
        else:
            # Check standalone learner skills without role
            for ls in learner_skills:
                curr_prof = float(ls.proficiency)
                if curr_prof < cls.MASTERY_CONTINUE:
                    severity = "critical" if curr_prof < cls.MASTERY_REINFORCEMENT else "moderate"
                    category = "FOUNDATIONAL_INTERVENTION" if curr_prof < cls.MASTERY_REINFORCEMENT else "TARGETED_REINFORCEMENT"
                    weak_skills.append({
                        "skill_id": ls.skill_id,
                        "skill_name": ls.skill.name if ls.skill else "Unknown",
                        "skill_slug": ls.skill.slug if ls.skill else "",
                        "current_proficiency": curr_prof,
                        "required_proficiency": 70.0,
                        "gap": round(max(0.0, 70.0 - curr_prof), 2),
                        "importance": 0.5,
                        "category": category,
                        "severity": severity
                    })

        # Sort weak skills: critical severity first, then gap DESC, importance DESC
        weak_skills.sort(
            key=lambda x: (
                0 if x["severity"] == "critical" else 1,
                -x["gap"],
                -x["importance"]
            )
        )
        return weak_skills

    @classmethod
    def select_interventions(
        cls,
        db: Session,
        weak_skills: List[Dict[str, Any]],
        learner_id: uuid.UUID
    ) -> List[AdaptiveIntervention]:
        """Select appropriate learning interventions matching weak skill severity (AI_SPEC.md §32, TECHNICAL.md §51)."""
        interventions: List[AdaptiveIntervention] = []

        all_resources = ResourceRepository.get_all(db)
        res_by_skill = defaultdict(list)
        for r in all_resources:
            for rs in r.resource_skills:
                res_by_skill[rs.skill_id].append(r)

        all_assessments = AssessmentRepository.get_all(db)
        assess_by_skill = {a.skill_id: a for a in all_assessments if a.skill_id}

        for ws in weak_skills:
            skill_id = ws["skill_id"]
            skill_name = ws["skill_name"]
            severity = ws["severity"]
            curr_prof = ws["current_proficiency"]

            cand_resources = res_by_skill.get(skill_id, [])
            # Filter beginner resources for critical weak skills, intermediate for moderate
            target_diff = "beginner" if severity == "critical" else "intermediate"
            chosen_res = next((r for r in cand_resources if r.difficulty == target_diff), None)
            if not chosen_res and cand_resources:
                chosen_res = cand_resources[0]

            chosen_assess = assess_by_skill.get(skill_id)

            if severity == "critical":
                # Foundational Intervention (< 40% mastery)
                interventions.append(
                    AdaptiveIntervention(
                        type="foundational_intervention",
                        skill_id=skill_id,
                        skill_name=skill_name,
                        severity="critical",
                        title=f"Foundational Reinforcement: {skill_name}",
                        description=f"Current mastery is {curr_prof:.1f}% (< {cls.MASTERY_REINFORCEMENT:.0f}% foundational threshold). Foundational study recommended before advanced topics.",
                        recommended_action=f"Review foundational concepts in '{chosen_res.title if chosen_res else skill_name}' and re-attempt practice.",
                        resource_id=chosen_res.id if chosen_res else None,
                        assessment_id=chosen_assess.id if chosen_assess else None
                    )
                )
            elif severity == "moderate":
                # Targeted Reinforcement (40% - 59% mastery)
                interventions.append(
                    AdaptiveIntervention(
                        type="refresher_resource",
                        skill_id=skill_id,
                        skill_name=skill_name,
                        severity="moderate",
                        title=f"Targeted Reinforcement: {skill_name}",
                        description=f"Current mastery is {curr_prof:.1f}%. A targeted refresher will help bridge the gap to target proficiency.",
                        recommended_action=f"Complete practice exercise in '{chosen_res.title if chosen_res else skill_name}'.",
                        resource_id=chosen_res.id if chosen_res else None,
                        assessment_id=chosen_assess.id if chosen_assess else None
                    )
                )

        return interventions

    @classmethod
    def adapt_roadmap_prerequisites(
        cls,
        db: Session,
        learner_id: uuid.UUID,
        roadmap: Roadmap
    ) -> Tuple[int, int, List[str]]:
        """Re-evaluate edge-specific prerequisite thresholds for all items in the active roadmap,

        transitioning items between LOCKED and AVAILABLE without destroying historical progress.
        """
        # Fetch updated learner proficiencies
        learner_skills = LearnerProfileRepository.get_learner_skills(db, learner_id)
        current_profs = {ls.skill_id: float(ls.proficiency) for ls in learner_skills}

        # Fetch target role requirements
        target_role_id = roadmap.target_role_id
        role_req_profs = {}
        if target_role_id:
            reqs = RoleRepository.get_role_skills(db, target_role_id)
            role_req_profs = {r.skill_id: float(r.required_proficiency) for r in reqs}

        all_skills_map = {s.id: s for s in SkillRepository.get_all(db)}
        all_prereqs = SkillRepository.get_all_prerequisites(db)
        prereqs_map = defaultdict(list)
        prereq_thresholds: Dict[Tuple[uuid.UUID, uuid.UUID], float] = {}

        for p in all_prereqs:
            prereqs_map[p.skill_id].append(p.prerequisite_skill_id)
            base_req = role_req_profs.get(p.prerequisite_skill_id, 70.0)
            prereq_thresholds[(p.skill_id, p.prerequisite_skill_id)] = round(
                float(p.strength) * base_req, 2
            )

        unlocked_count = 0
        locked_count = 0
        status_changes: List[str] = []

        for item in roadmap.items:
            # Skip completed items
            if item.status == "COMPLETED":
                continue

            if not item.skill_id:
                continue

            direct_prereqs = prereqs_map.get(item.skill_id, [])
            unmet_prereq_names = []

            for p_id in direct_prereqs:
                req_threshold = prereq_thresholds.get((item.skill_id, p_id), 70.0)
                p_prof = current_profs.get(p_id, 0.0)
                if p_prof < req_threshold:
                    p_skill = all_skills_map.get(p_id)
                    if p_skill:
                        unmet_prereq_names.append(f"{p_skill.name} (>= {req_threshold:.0f}%)")

            skill_name = item.skill.name if item.skill else "Skill"

            if not unmet_prereq_names:
                # All prerequisites are satisfied
                if item.status == "LOCKED":
                    item.status = "AVAILABLE"
                    item.locked_reason = None
                    db.add(item)
                    unlocked_count += 1
                    status_changes.append(f"Unlocked step: '{skill_name}' (all prerequisites satisfied)")
            else:
                # Prerequisites not satisfied
                lock_msg = f"Requires prerequisite(s): {', '.join(unmet_prereq_names)}"
                if item.status in ["AVAILABLE", "IN_PROGRESS"]:
                    item.status = "LOCKED"
                    item.locked_reason = lock_msg
                    db.add(item)
                    locked_count += 1
                    status_changes.append(f"Locked step: '{skill_name}' ({lock_msg})")
                elif item.status == "LOCKED" and item.locked_reason != lock_msg:
                    item.locked_reason = lock_msg
                    db.add(item)

        return unlocked_count, locked_count, status_changes

    @classmethod
    def get_next_best_action(
        cls,
        db: Session,
        user_id: uuid.UUID,
        active_interventions: Optional[List[AdaptiveIntervention]] = None
    ) -> Optional[NextBestActionResponse]:
        """Compute the highest-priority, actionable next step for the learner.

        Priority Order (API_SPEC.md §14, AI_ARCH.md §49):
        1. Required Critical Intervention
        2. Current In-Progress Roadmap Item
        3. Next Available Roadmap Item (lowest sequence)
        4. High-Priority Skill Gap / Pending Assessment
        """
        profile = LearnerProfileRepository.get_by_user_id(db, user_id)
        if not profile:
            return None

        # Priority 1: Critical Intervention
        if active_interventions:
            crit_intervention = next(
                (i for i in active_interventions if i.severity == "critical"),
                None
            )
            if crit_intervention:
                res_summary = None
                if crit_intervention.resource_id:
                    r_obj = ResourceRepository.get_by_id(db, crit_intervention.resource_id)
                    if r_obj:
                        res_summary = ResourceSummary(
                            id=r_obj.id,
                            title=r_obj.title,
                            url=r_obj.url,
                            resource_type=r_obj.resource_type,
                            provider=r_obj.provider,
                            difficulty=r_obj.difficulty,
                            estimated_hours=round(float(r_obj.estimated_minutes) / 60.0, 2) if r_obj.estimated_minutes else None,
                            quality_score=float(r_obj.quality_score) if r_obj.quality_score else None,
                            is_free=bool(r_obj.meta_data.get("is_free", True)) if isinstance(r_obj.meta_data, dict) else True,
                            skills_covered=[crit_intervention.skill_name]
                        )

                return NextBestActionResponse(
                    id=crit_intervention.resource_id or crit_intervention.assessment_id,
                    skill_id=crit_intervention.skill_id,
                    skill_name=crit_intervention.skill_name,
                    action_type="intervention",
                    title=crit_intervention.title,
                    reason=crit_intervention.description,
                    estimated_hours=res_summary.estimated_hours if res_summary else 1.0,
                    resource=res_summary,
                    status="RECOMMENDED"
                )

        # Priority 2 & 3: Active Roadmap Items (IN_PROGRESS first, then AVAILABLE)
        roadmap = RoadmapRepository.get_active_roadmap(db, profile.id)
        if roadmap and roadmap.items:
            # Check IN_PROGRESS item
            in_prog_item = next(
                (item for item in roadmap.items if item.status == "IN_PROGRESS"),
                None
            )
            if in_prog_item:
                return cls._serialize_roadmap_item_as_next_action(in_prog_item, action_type="study_item")

            # Check lowest sequence AVAILABLE item
            avail_items = [item for item in roadmap.items if item.status == "AVAILABLE"]
            avail_items.sort(key=lambda x: x.sequence)
            if avail_items:
                return cls._serialize_roadmap_item_as_next_action(avail_items[0], action_type="study_item")

        # Priority 4: Dynamic Skill Gap / Recommendations
        if profile.target_role_id:
            gaps_data = SkillGapService.analyze_gaps(db, user_id)
            if gaps_data.skills:
                top_gap = gaps_data.skills[0]
                if top_gap.gap > 0:
                    return NextBestActionResponse(
                        id=None,
                        skill_id=top_gap.skill_id,
                        skill_name=top_gap.skill,
                        action_type="assessment",
                        title=f"Assess / Bridge Gap: {top_gap.skill}",
                        reason=f"Top skill gap for your target role (Gap: {top_gap.gap:.0f}%, Importance: {top_gap.importance:.2f}).",
                        estimated_hours=2.0,
                        resource=None,
                        status="RECOMMENDED"
                    )

        return None

    @classmethod
    def on_assessment_completed(
        cls,
        db: Session,
        user_id: uuid.UUID,
        assessment_id: uuid.UUID,
        score: float,
        mastery: float
    ) -> Dict[str, Any]:
        """Triggered automatically when an assessment submission completes within the same transaction."""
        assessment = AssessmentRepository.get_by_id(db, assessment_id)
        skill_name = assessment.skill.name if assessment and assessment.skill else "Skill"

        eval_resp = cls.evaluate_and_adapt(
            db=db,
            user_id=user_id,
            trigger_event="ASSESSMENT",
            context={
                "assessment_id": str(assessment_id),
                "skill_name": skill_name,
                "score": score,
                "mastery": mastery
            }
        )

        return {
            "roadmap_updated": eval_resp.roadmap_updated,
            "unlocked_items": eval_resp.unlocked_items_count,
            "locked_items": eval_resp.locked_items_count,
            "interventions_count": len(eval_resp.interventions),
            "reason": eval_resp.reason
        }

    @classmethod
    def on_target_role_changed(
        cls,
        db: Session,
        user_id: uuid.UUID,
        old_role_id: Optional[uuid.UUID],
        new_role_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Triggered when a learner updates their target career role."""
        eval_resp = cls.evaluate_and_adapt(
            db=db,
            user_id=user_id,
            trigger_event="ROLE_CHANGE",
            context={
                "old_role_id": str(old_role_id) if old_role_id else None,
                "new_role_id": str(new_role_id)
            }
        )

        return {
            "roadmap_updated": eval_resp.roadmap_updated,
            "roadmap_version": eval_resp.roadmap_version,
            "reason": eval_resp.reason
        }

    @classmethod
    def on_skill_proficiency_updated(
        cls,
        db: Session,
        user_id: uuid.UUID,
        skill_id: uuid.UUID,
        old_proficiency: float,
        new_proficiency: float
    ) -> Dict[str, Any]:
        """Triggered when a learner skill is added or updated."""
        skill = SkillRepository.get_by_id(db, skill_id)
        skill_name = skill.name if skill else "Skill"

        eval_resp = cls.evaluate_and_adapt(
            db=db,
            user_id=user_id,
            trigger_event="PROFICIENCY_UPDATE",
            context={
                "skill_id": str(skill_id),
                "skill_name": skill_name,
                "old_proficiency": old_proficiency,
                "new_proficiency": new_proficiency
            }
        )

        return {
            "roadmap_updated": eval_resp.roadmap_updated,
            "unlocked_items": eval_resp.unlocked_items_count,
            "locked_items": eval_resp.locked_items_count,
            "reason": eval_resp.reason
        }

    @staticmethod
    def _serialize_roadmap_item_as_next_action(
        item: RoadmapItem,
        action_type: str = "study_item"
    ) -> NextBestActionResponse:
        """Helper to serialize a RoadmapItem into NextBestActionResponse."""
        res_summary = None
        if item.resource:
            res_summary = ResourceSummary(
                id=item.resource.id,
                title=item.resource.title,
                url=item.resource.url,
                resource_type=item.resource.resource_type,
                provider=item.resource.provider,
                difficulty=item.resource.difficulty,
                estimated_hours=round(float(item.resource.estimated_minutes) / 60.0, 2) if item.resource.estimated_minutes else None,
                quality_score=float(item.resource.quality_score) if item.resource.quality_score else None,
                is_free=bool(item.resource.meta_data.get("is_free", True)) if isinstance(item.resource.meta_data, dict) else True,
                skills_covered=[item.skill.name] if item.skill else []
            )

        title = f"Step {item.sequence}: {item.skill.name if item.skill else 'Milestone'}"
        if item.resource:
            title = f"{item.skill.name if item.skill else 'Study'}: {item.resource.title}"

        reason = (
            item.reason.get("explanation", "Next recommended milestone in your roadmap.")
            if isinstance(item.reason, dict)
            else "Next recommended milestone in your roadmap."
        )

        return NextBestActionResponse(
            id=item.id,
            skill_id=item.skill_id,
            skill_name=item.skill.name if item.skill else None,
            action_type=action_type,
            title=title,
            reason=reason,
            estimated_hours=float(item.estimated_hours) if item.estimated_hours else None,
            resource=res_summary,
            status=item.status
        )
