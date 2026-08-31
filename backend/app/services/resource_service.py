import math
import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload, joinedload

from backend.app.models.resource import Resource
from backend.app.models.resource_skill import ResourceSkill
from backend.app.models.skill import Skill
from backend.app.schemas.resource import (
    ResourceItemResponse,
    ResourceDetailResponse,
    ResourceSkillSummary,
    PaginatedResourcesResponse,
)
from backend.app.core.exceptions import NotFoundError


class ResourceService:
    """Service handling catalog browsing, filtering, and detail retrieval for curated learning resources."""

    @staticmethod
    def list_resources(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        skill_id: Optional[uuid.UUID] = None,
        difficulty: Optional[str] = None,
        resource_type: Optional[str] = None,
        provider: Optional[str] = None,
        search: Optional[str] = None
    ) -> PaginatedResourcesResponse:
        """List active resources with pagination and optional filtering."""
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        offset = (page - 1) * page_size

        # Base query for counting and fetching active resources
        base_query = select(Resource).where(Resource.is_active == True)

        if skill_id:
            base_query = base_query.join(Resource.resource_skills).where(ResourceSkill.skill_id == skill_id)

        if difficulty:
            base_query = base_query.where(func.lower(Resource.difficulty) == difficulty.lower().strip())

        if resource_type:
            base_query = base_query.where(func.lower(Resource.resource_type) == resource_type.lower().strip())

        if provider:
            base_query = base_query.where(func.lower(Resource.provider) == provider.lower().strip())

        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            base_query = base_query.where(
                func.lower(Resource.title).like(term) | func.lower(Resource.description).like(term)
            )

        # Count total
        subq = base_query.subquery()
        count_stmt = select(func.count()).select_from(subq)
        total = db.execute(count_stmt).scalar() or 0

        # Fetch items ordered deterministically
        fetch_stmt = (
            base_query.options(
                selectinload(Resource.resource_skills).joinedload(ResourceSkill.skill)
            )
            .distinct()
            .order_by(Resource.quality_score.desc(), Resource.title.asc(), Resource.id.asc())
            .offset(offset)
            .limit(page_size)
        )

        resources = db.execute(fetch_stmt).scalars().all()

        items = []
        for r in resources:
            skills = [
                ResourceSkillSummary(
                    id=rs.skill.id,
                    name=rs.skill.name,
                    slug=rs.skill.slug,
                    category=rs.skill.category
                )
                for rs in r.resource_skills
                if rs.skill
            ]
            items.append(
                ResourceItemResponse(
                    id=r.id,
                    title=r.title,
                    description=r.description,
                    resource_type=r.resource_type,
                    provider=r.provider,
                    url=r.url,
                    difficulty=r.difficulty,
                    estimated_minutes=r.estimated_minutes,
                    quality_score=float(r.quality_score) if r.quality_score is not None else 0.0,
                    is_active=r.is_active,
                    skills=skills,
                    metadata=r.meta_data
                )
            )

        total_pages = math.ceil(total / page_size) if total > 0 else 1

        return PaginatedResourcesResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    @staticmethod
    def get_resource_by_id(db: Session, resource_id: uuid.UUID) -> ResourceDetailResponse:
        """Fetch a single resource by ID with associated skills, verifying it is active."""
        stmt = (
            select(Resource)
            .options(
                selectinload(Resource.resource_skills).joinedload(ResourceSkill.skill)
            )
            .where(Resource.id == resource_id, Resource.is_active == True)
        )
        resource = db.execute(stmt).scalar_one_or_none()
        if not resource:
            raise NotFoundError(f"Resource with ID {resource_id} not found or inactive")

        skills = [
            ResourceSkillSummary(
                id=rs.skill.id,
                name=rs.skill.name,
                slug=rs.skill.slug,
                category=rs.skill.category
            )
            for rs in resource.resource_skills
            if rs.skill
        ]

        return ResourceDetailResponse(
            id=resource.id,
            title=resource.title,
            description=resource.description,
            resource_type=resource.resource_type,
            provider=resource.provider,
            url=resource.url,
            difficulty=resource.difficulty,
            estimated_minutes=resource.estimated_minutes,
            quality_score=float(resource.quality_score) if resource.quality_score is not None else 0.0,
            is_active=resource.is_active,
            skills=skills,
            metadata=resource.meta_data
        )
