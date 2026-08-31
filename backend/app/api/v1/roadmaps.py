import uuid
from typing import Optional
from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.api.deps import get_current_active_user
from backend.app.models.user import User
from backend.app.services.roadmap_service import RoadmapService
from backend.app.schemas.common import APIResponse
from backend.app.schemas.roadmap import (
    RoadmapGenerateRequest, RoadmapResponse,
    RoadmapSummaryResponse, RoadmapItemResponse
)

router = APIRouter(prefix="/roadmaps", tags=["Roadmaps"])


@router.post(
    "/generate",
    response_model=APIResponse[RoadmapResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate a dependency-aware personalized roadmap"
)
def generate_roadmap(
    generate_in: Optional[RoadmapGenerateRequest] = Body(default=None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a topologically-ordered, personalized learning roadmap based on target role, skill gaps, and prerequisites."""
    roadmap = RoadmapService.generate_roadmap(
        db=db,
        user_id=current_user.id,
        generate_in=generate_in
    )
    return APIResponse(
        success=True,
        data=roadmap,
        message="Roadmap generated successfully"
    )


@router.get(
    "/current",
    response_model=APIResponse[RoadmapSummaryResponse],
    summary="Get current active roadmap and next best action"
)
def get_current_roadmap(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Retrieve the learner's active roadmap, overall progress metrics, and the next actionable learning step."""
    summary = RoadmapService.get_current_roadmap(
        db=db,
        user_id=current_user.id
    )
    return APIResponse(
        success=True,
        data=summary,
        message="Current roadmap retrieved successfully"
    )


@router.get(
    "/items/{item_id}",
    response_model=APIResponse[RoadmapItemResponse],
    summary="Get roadmap item details"
)
def get_roadmap_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Retrieve details, learning resources, and completion status of a single roadmap step."""
    item = RoadmapService.get_roadmap_item_by_id(
        db=db,
        user_id=current_user.id,
        item_id=item_id
    )
    return APIResponse(
        success=True,
        data=item,
        message="Roadmap item retrieved successfully"
    )


@router.post(
    "/items/{item_id}/start",
    response_model=APIResponse[RoadmapItemResponse],
    summary="Start a roadmap item"
)
def start_roadmap_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Transition an available roadmap step to in-progress status."""
    item = RoadmapService.start_roadmap_item(
        db=db,
        user_id=current_user.id,
        item_id=item_id
    )
    return APIResponse(
        success=True,
        data=item,
        message="Roadmap item started successfully"
    )


@router.post(
    "/items/{item_id}/complete",
    response_model=APIResponse[RoadmapItemResponse],
    summary="Complete a roadmap item and unlock dependent steps"
)
def complete_roadmap_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Complete a learning step, update progress and skill mastery, and unlock any downstream prerequisite-dependent steps."""
    item = RoadmapService.complete_roadmap_item(
        db=db,
        user_id=current_user.id,
        item_id=item_id
    )
    return APIResponse(
        success=True,
        data=item,
        message="Roadmap item completed successfully"
    )


@router.get(
    "/{roadmap_id}",
    response_model=APIResponse[RoadmapResponse],
    summary="Get specific roadmap by ID"
)
def get_roadmap_by_id(
    roadmap_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Retrieve full roadmap details for a specific roadmap ID."""
    roadmap = RoadmapService.get_roadmap_by_id(
        db=db,
        user_id=current_user.id,
        roadmap_id=roadmap_id
    )
    return APIResponse(
        success=True,
        data=roadmap,
        message="Roadmap retrieved successfully"
    )


@router.post(
    "/{roadmap_id}/recalculate",
    response_model=APIResponse[RoadmapResponse],
    summary="Recalculate roadmap and create a new version"
)
def recalculate_roadmap(
    roadmap_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Recalculate roadmap after profile, assessment, or proficiency changes, preserving historical version snapshots."""
    roadmap = RoadmapService.generate_roadmap(
        db=db,
        user_id=current_user.id
    )
    return APIResponse(
        success=True,
        data=roadmap,
        message="Roadmap recalculated successfully"
    )
