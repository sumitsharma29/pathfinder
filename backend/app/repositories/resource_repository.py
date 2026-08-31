import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload
from backend.app.models.resource import Resource
from backend.app.models.resource_skill import ResourceSkill


class ResourceRepository:
    """Repository handling database operations for learning resources."""

    @staticmethod
    def get_all(
        db: Session,
        skill_id: Optional[uuid.UUID] = None,
        resource_type: Optional[str] = None
    ) -> List[Resource]:
        """Fetch active resources with associated skills."""
        query = (
            select(Resource)
            .options(
                selectinload(Resource.resource_skills).joinedload(ResourceSkill.skill)
            )
            .where(Resource.is_active == True)
        )
        if resource_type:
            query = query.where(Resource.resource_type == resource_type)

        if skill_id:
            query = query.join(Resource.resource_skills).where(ResourceSkill.skill_id == skill_id)

        return db.execute(query).scalars().all()

    @staticmethod
    def get_by_id(db: Session, resource_id: uuid.UUID) -> Optional[Resource]:
        """Fetch resource by ID with associated skills."""
        return db.execute(
            select(Resource)
            .options(
                selectinload(Resource.resource_skills).joinedload(ResourceSkill.skill)
            )
            .where(Resource.id == resource_id)
        ).scalar_one_or_none()

    @staticmethod
    def get_resources_for_skills(db: Session, skill_ids: List[uuid.UUID]) -> List[Resource]:
        """Fetch active resources that teach any of the specified skills."""
        if not skill_ids:
            return []

        return db.execute(
            select(Resource)
            .options(
                selectinload(Resource.resource_skills).joinedload(ResourceSkill.skill)
            )
            .join(Resource.resource_skills)
            .where(
                Resource.is_active == True,
                ResourceSkill.skill_id.in_(skill_ids)
            )
            .distinct()
        ).scalars().all()
