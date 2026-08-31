import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.common import APIResponse
from backend.app.schemas.resource import (
    ResourceDetailResponse,
    PaginatedResourcesResponse,
)
from backend.app.services.resource_service import ResourceService

router = APIRouter(prefix="/resources", tags=["Learning Resources"])


@router.get(
    "",
    response_model=APIResponse[PaginatedResourcesResponse],
    summary="List curated learning resources with filtering and pagination"
)
def list_resources(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    skill_id: Optional[uuid.UUID] = Query(None, description="Filter by covered skill ID"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (beginner, intermediate, advanced)"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type (course, article, video, project, tutorial)"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    search: Optional[str] = Query(None, description="Search by title or description"),
    db: Session = Depends(get_db)
):
    """Retrieve active curated learning resources with optional filtering and pagination."""
    data = ResourceService.list_resources(
        db=db,
        page=page,
        page_size=page_size,
        skill_id=skill_id,
        difficulty=difficulty,
        resource_type=resource_type,
        provider=provider,
        search=search
    )
    return APIResponse(
        success=True,
        data=data,
        message="Resources retrieved successfully"
    )


@router.get(
    "/{id}",
    response_model=APIResponse[ResourceDetailResponse],
    summary="Get detailed view of a specific learning resource"
)
def get_resource_by_id(
    id: uuid.UUID = Path(..., description="Resource ID"),
    db: Session = Depends(get_db)
):
    """Retrieve detailed metadata and skills covered for a specific active resource."""
    resource = ResourceService.get_resource_by_id(db=db, resource_id=id)
    return APIResponse(
        success=True,
        data=resource,
        message="Resource retrieved successfully"
    )
