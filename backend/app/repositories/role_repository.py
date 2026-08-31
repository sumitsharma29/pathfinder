import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from backend.app.models.role import Role
from backend.app.models.role_skill import RoleSkill


class RoleRepository:
    """Repository handling read-only role catalog and role skill requirements."""

    @staticmethod
    def get_all(db: Session) -> List[Role]:
        """Fetch all roles in the catalog."""
        return db.execute(select(Role).order_by(Role.name)).scalars().all()

    @staticmethod
    def get_by_id(db: Session, role_id: uuid.UUID) -> Optional[Role]:
        """Fetch role by ID."""
        return db.execute(select(Role).where(Role.id == role_id)).scalar_one_or_none()

    @staticmethod
    def get_by_slug(db: Session, slug: str) -> Optional[Role]:
        """Fetch role by slug."""
        return db.execute(select(Role).where(Role.slug == slug)).scalar_one_or_none()

    @staticmethod
    def get_role_skills(db: Session, role_id: uuid.UUID) -> List[RoleSkill]:
        """Fetch all required skills for a role with skill details."""
        return db.execute(
            select(RoleSkill)
            .options(joinedload(RoleSkill.skill))
            .where(RoleSkill.role_id == role_id)
            .order_by(RoleSkill.importance.desc())
        ).scalars().all()
