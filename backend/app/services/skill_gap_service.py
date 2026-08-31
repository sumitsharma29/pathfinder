import uuid
from typing import List, Dict, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from backend.app.core.exceptions import NotFoundError
from backend.app.repositories.learner_profile_repository import LearnerProfileRepository
from backend.app.repositories.role_repository import RoleRepository
from backend.app.repositories.skill_repository import SkillRepository
from backend.app.schemas.skill_gap import (
    SkillGapItem, SkillGapSummary, SkillGapAnalysisData
)


class SkillGapService:
    """Dynamic Skill Gap Engine.
    Deterministically computes skill gaps on-the-fly from role_skills and learner_skills.
    Zero persistence, no static skill_gaps table.
    """

    @classmethod
    def analyze_gaps(
        cls,
        db: Session,
        user_id: uuid.UUID,
        override_role_id: Optional[uuid.UUID] = None
    ) -> SkillGapAnalysisData:
        """Analyze and calculate gaps for authenticated learner against target role."""
        # 1. Fetch learner profile
        profile = LearnerProfileRepository.get_by_user_id(db, user_id)
        if not profile:
            raise NotFoundError(message="Learner profile not found")

        # 2. Determine target role
        target_role_id = override_role_id or profile.target_role_id
        if not target_role_id:
            raise NotFoundError(
                message="No target role selected. Please set a target career role in your profile first."
            )

        role = RoleRepository.get_by_id(db, target_role_id)
        if not role:
            raise NotFoundError(
                message="Target career role does not exist",
                details={"target_role_id": str(target_role_id)}
            )

        # 3. Retrieve role requirements
        role_skills = RoleRepository.get_role_skills(db, target_role_id)
        if not role_skills:
            return SkillGapAnalysisData(
                target_role_id=role.id,
                target_role=role.name,
                summary=SkillGapSummary(
                    total_skills_required=0,
                    skills_mastered=0,
                    skills_in_progress=0,
                    skills_missing=0,
                    average_gap=0.0,
                    overall_readiness_percentage=0.0
                ),
                skills=[]
            )

        # 4. Retrieve current learner skills map
        learner_skills_list = LearnerProfileRepository.get_learner_skills(db, profile.id)
        learner_skills_map: Dict[uuid.UUID, float] = {
            ls.skill_id: float(ls.proficiency) for ls in learner_skills_list
        }

        # 5. Retrieve prerequisite relationships for dependency awareness
        all_prereqs = SkillRepository.get_all_prerequisites(db)
        prereqs_map = defaultdict(list)
        for p in all_prereqs:
            prereqs_map[p.skill_id].append(
                p.prerequisite_skill.name if p.prerequisite_skill else "Prerequisite"
            )

        # 6. Calculate gaps deterministically
        gap_items: List[SkillGapItem] = []
        total_required_points = 0.0
        total_acquired_points = 0.0
        total_gap = 0.0

        for rs in role_skills:
            skill = rs.skill
            if not skill:
                continue

            required_prof = float(rs.required_proficiency)
            importance = float(rs.importance)
            current_prof = float(learner_skills_map.get(skill.id, 0.0))

            # Ensure current proficiency does not exceed 100
            current_prof = min(max(current_prof, 0.0), 100.0)

            # Calculate gap: max(required - current, 0)
            gap = max(required_prof - current_prof, 0.0)
            
            # Status determination
            if current_prof >= required_prof:
                status = "MASTERED"
            elif current_prof > 0:
                status = "PARTIAL"
            else:
                status = "MISSING"

            # Priority calculation: (gap / 100) * importance
            gap_weight = gap / 100.0
            priority = round(gap_weight * importance, 4)

            total_required_points += required_prof
            total_acquired_points += min(current_prof, required_prof)
            total_gap += gap

            gap_items.append(
                SkillGapItem(
                    skill_id=skill.id,
                    skill=skill.name,
                    skill_slug=skill.slug,
                    category=skill.category,
                    required=required_prof,
                    current=current_prof,
                    gap=gap,
                    importance=importance,
                    priority=priority,
                    status=status,
                    prerequisites=prereqs_map.get(skill.id, [])
                )
            )

        # 7. Sort items: highest priority first, then importance descending
        gap_items.sort(key=lambda x: (x.priority, x.importance, x.gap), reverse=True)

        # 8. Compute summary metrics
        total_count = len(gap_items)
        mastered_count = sum(1 for item in gap_items if item.status == "MASTERED")
        partial_count = sum(1 for item in gap_items if item.status == "PARTIAL")
        missing_count = sum(1 for item in gap_items if item.status == "MISSING")
        avg_gap = round(total_gap / total_count, 2) if total_count > 0 else 0.0
        readiness_pct = (
            round((total_acquired_points / total_required_points) * 100.0, 2)
            if total_required_points > 0 else 0.0
        )

        summary = SkillGapSummary(
            total_skills_required=total_count,
            skills_mastered=mastered_count,
            skills_in_progress=partial_count,
            skills_missing=missing_count,
            average_gap=avg_gap,
            overall_readiness_percentage=readiness_pct
        )

        return SkillGapAnalysisData(
            target_role_id=role.id,
            target_role=role.name,
            summary=summary,
            skills=gap_items
        )
