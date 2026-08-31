import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from backend.app.models.skill import Skill
from backend.app.models.skill_prerequisite import SkillPrerequisite


class SkillRepository:
    """Repository handling read-only global skill catalog and prerequisite graph operations."""

    @staticmethod
    def get_all(db: Session, category: Optional[str] = None) -> List[Skill]:
        """Fetch all skills in catalog, optionally filtered by category."""
        query = select(Skill).order_by(Skill.name)
        if category:
            query = query.where(Skill.category.ilike(f"%{category}%"))
        return db.execute(query).scalars().all()

    @staticmethod
    def get_by_id(db: Session, skill_id: uuid.UUID) -> Optional[Skill]:
        """Fetch skill by ID."""
        return db.execute(select(Skill).where(Skill.id == skill_id)).scalar_one_or_none()

    @staticmethod
    def get_by_slug(db: Session, slug: str) -> Optional[Skill]:
        """Fetch skill by slug."""
        return db.execute(select(Skill).where(Skill.slug == slug)).scalar_one_or_none()

    @staticmethod
    def get_prerequisites_for_skill(db: Session, skill_id: uuid.UUID) -> List[SkillPrerequisite]:
        """Fetch direct prerequisites for a skill (skills that must be learned BEFORE this skill)."""
        return db.execute(
            select(SkillPrerequisite)
            .options(
                joinedload(SkillPrerequisite.skill),
                joinedload(SkillPrerequisite.prerequisite_skill)
            )
            .where(SkillPrerequisite.skill_id == skill_id)
        ).scalars().all()

    @staticmethod
    def get_dependent_skills(db: Session, skill_id: uuid.UUID) -> List[SkillPrerequisite]:
        """Fetch skills that depend ON this prerequisite skill."""
        return db.execute(
            select(SkillPrerequisite)
            .options(
                joinedload(SkillPrerequisite.skill),
                joinedload(SkillPrerequisite.prerequisite_skill)
            )
            .where(SkillPrerequisite.prerequisite_skill_id == skill_id)
        ).scalars().all()

    @staticmethod
    def get_all_prerequisites(db: Session) -> List[SkillPrerequisite]:
        """Fetch the entire prerequisite dependency graph."""
        return db.execute(
            select(SkillPrerequisite)
            .options(
                joinedload(SkillPrerequisite.skill),
                joinedload(SkillPrerequisite.prerequisite_skill)
            )
        ).scalars().all()
