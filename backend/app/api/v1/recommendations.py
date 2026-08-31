import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.api.deps import get_current_active_user
from backend.app.models.user import User
from backend.app.services.recommendation_service import RecommendationService
from backend.app.schemas.common import APIResponse
from backend.app.schemas.recommendation import (
    RecommendationItem, RecommendationListResponse,
    RecommendationDetailResponse, FeedbackCreateRequest, FeedbackResponse
)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get(
    "",
    response_model=RecommendationListResponse,
    summary="Get personalized learning recommendations"
)
def get_recommendations(
    skill_id: Optional[uuid.UUID] = Query(None, description="Filter recommendations by skill"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type (e.g. course, video, project)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Retrieve personalized, prerequisite-aware learning recommendations for the authenticated learner."""
    items = RecommendationService.get_recommendations(
        db=db,
        user_id=current_user.id,
        skill_id=skill_id,
        resource_type=resource_type,
        limit=page_size,
        page=page,
        page_size=page_size
    )
    return RecommendationListResponse(
        success=True,
        data=items,
        message="Recommendations retrieved successfully"
    )


@router.get(
    "/{id}",
    response_model=RecommendationDetailResponse,
    summary="Get recommendation details and explainability breakdown"
)
def get_recommendation_by_id(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Retrieve a single recommendation and its complete scoring breakdown."""
    item = RecommendationService.get_recommendation_by_id(
        db=db,
        user_id=current_user.id,
        recommendation_id=id
    )
    return RecommendationDetailResponse(
        success=True,
        data=item,
        message="Recommendation retrieved successfully"
    )


@router.post(
    "/{id}/feedback",
    response_model=APIResponse[FeedbackResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit feedback on a recommendation"
)
def submit_recommendation_feedback(
    id: uuid.UUID,
    feedback_in: FeedbackCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit learner feedback (helpful, not_helpful, rating, comments) for a recommendation."""
    fb = RecommendationService.submit_feedback(
        db=db,
        user_id=current_user.id,
        recommendation_id=id,
        feedback_in=feedback_in
    )
    return APIResponse(
        success=True,
        data=fb,
        message="Feedback submitted successfully"
    )
