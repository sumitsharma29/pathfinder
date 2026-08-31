import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.api.deps import get_current_active_user
from backend.app.models.user import User
from backend.app.services.assessment_service import AssessmentService
from backend.app.schemas.common import APIResponse
from backend.app.schemas.assessment import (
    AssessmentSummary, AssessmentDetailResponse,
    AssessmentSubmissionRequest, AssessmentResultResponse,
    AssessmentHistoryItem
)

router = APIRouter(prefix="/assessments", tags=["Assessments"])


@router.get(
    "",
    response_model=APIResponse[List[AssessmentSummary]],
    summary="List available assessments in catalog"
)
def list_assessments(
    skill_id: Optional[uuid.UUID] = Query(default=None, description="Filter assessments by skill ID"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Retrieve all available skill assessments in the global catalog."""
    assessments = AssessmentService.list_assessments(
        db=db,
        skill_id=skill_id,
        page=page,
        page_size=page_size
    )
    return APIResponse(
        success=True,
        data=assessments,
        message="Assessments retrieved successfully"
    )


@router.get(
    "/results",
    response_model=APIResponse[List[AssessmentHistoryItem]],
    summary="Get learner assessment history"
)
def get_assessment_results(
    assessment_id: Optional[uuid.UUID] = Query(default=None, description="Filter history by assessment ID"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Retrieve historical assessment results for the authenticated learner."""
    results = AssessmentService.get_learner_results(
        db=db,
        user_id=current_user.id,
        assessment_id=assessment_id,
        page=page,
        page_size=page_size
    )
    return APIResponse(
        success=True,
        data=results,
        message="Assessment results retrieved successfully"
    )


@router.get(
    "/{assessment_id}",
    response_model=APIResponse[AssessmentDetailResponse],
    summary="Get assessment details and questions"
)
def get_assessment_detail(
    assessment_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Retrieve assessment details and questions for taking the assessment. Answer keys are strictly excluded."""
    detail = AssessmentService.get_assessment_detail(
        db=db,
        assessment_id=assessment_id
    )
    return APIResponse(
        success=True,
        data=detail,
        message="Assessment retrieved successfully"
    )


@router.post(
    "/{assessment_id}/submit",
    response_model=APIResponse[AssessmentResultResponse],
    status_code=status.HTTP_200_OK,
    summary="Submit assessment answers for server-side scoring"
)
def submit_assessment(
    assessment_id: uuid.UUID,
    submission: AssessmentSubmissionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit answers for an assessment. Evaluates score server-side, updates skill mastery, and records immutable result."""
    result = AssessmentService.submit_assessment(
        db=db,
        user_id=current_user.id,
        assessment_id=assessment_id,
        submission=submission
    )
    return APIResponse(
        success=True,
        data=result,
        message="Assessment submitted successfully"
    )
