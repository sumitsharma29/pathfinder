import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.core.exceptions import NotFoundError
from backend.app.repositories.skill_repository import SkillRepository
from backend.app.schemas.skill import SkillResponse, SkillPrerequisiteResponse, SkillDetailResponse
from backend.app.models.skill import Skill


class SkillService:
    """Service handling read-only skill catalog and prerequisite graph retrieval."""

    @staticmethod
    def list_skills(db: Session, category: Optional[str] = None) -> List[SkillResponse]:
        """List all skills in global catalog."""
        skills = SkillRepository.get_all(db, category)
        return [
            SkillResponse(
                id=s.id,
                name=s.name,
                slug=s.slug,
                category=s.category,
                description=s.description,
                difficulty=s.difficulty,
                estimated_hours=float(s.estimated_hours) if s.estimated_hours is not None else None
            )
            for s in skills
        ]

    @staticmethod
    def get_skill(db: Session, skill_id: uuid.UUID) -> SkillDetailResponse:
        """Get detailed skill information with direct prerequisites."""
        skill = SkillRepository.get_by_id(db, skill_id)
        if not skill:
            raise NotFoundError(message="Skill not found", details={"skill_id": str(skill_id)})

        prereqs = SkillRepository.get_prerequisites_for_skill(db, skill_id)
        dependents = SkillRepository.get_dependent_skills(db, skill_id)

        prereq_items = [
            SkillPrerequisiteResponse(
                skill_id=p.skill_id,
                skill_name=p.skill.name if p.skill else "",
                prerequisite_skill_id=p.prerequisite_skill_id,
                prerequisite_skill_name=p.prerequisite_skill.name if p.prerequisite_skill else "",
                prerequisite_skill_slug=p.prerequisite_skill.slug if p.prerequisite_skill else "",
                strength=float(p.strength)
            )
            for p in prereqs
        ]

        dependent_items = [
            SkillPrerequisiteResponse(
                skill_id=d.skill_id,
                skill_name=d.skill.name if d.skill else "",
                prerequisite_skill_id=d.prerequisite_skill_id,
                prerequisite_skill_name=d.prerequisite_skill.name if d.prerequisite_skill else "",
                prerequisite_skill_slug=d.prerequisite_skill.slug if d.prerequisite_skill else "",
                strength=float(d.strength)
            )
            for d in dependents
        ]

        return SkillDetailResponse(
            id=skill.id,
            name=skill.name,
            slug=skill.slug,
            category=skill.category,
            description=skill.description,
            difficulty=skill.difficulty,
            estimated_hours=float(skill.estimated_hours) if skill.estimated_hours is not None else None,
            prerequisites=prereq_items,
            dependent_skills=dependent_items
        )

    @staticmethod
    def get_prerequisites(db: Session, skill_id: uuid.UUID) -> List[SkillPrerequisiteResponse]:
        """Fetch prerequisite relationships for a specific skill."""
        skill = SkillRepository.get_by_id(db, skill_id)
        if not skill:
            raise NotFoundError(message="Skill not found", details={"skill_id": str(skill_id)})

        prereqs = SkillRepository.get_prerequisites_for_skill(db, skill_id)
        return [
            SkillPrerequisiteResponse(
                skill_id=p.skill_id,
                skill_name=p.skill.name if p.skill else "",
                prerequisite_skill_id=p.prerequisite_skill_id,
                prerequisite_skill_name=p.prerequisite_skill.name if p.prerequisite_skill else "",
                prerequisite_skill_slug=p.prerequisite_skill.slug if p.prerequisite_skill else "",
                strength=float(p.strength)
            )
            for p in prereqs
        ]
