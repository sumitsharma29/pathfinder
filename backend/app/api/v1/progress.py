import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.api.deps import get_current_active_user
from backend.app.models.user import User
from backend.app.services.adaptive_learning_service import AdaptiveLearningService
from backend.app.services.progress_service import ProgressService
from backend.app.schemas.common import APIResponse
from backend.app.schemas.adaptive import NextBestActionResponse
from backend.app.schemas.progress import (
    OverallProgressResponse,
    SkillProgressItem,
    MilestoneProgressItem,
    DashboardAggregationResponse,
)

router = APIRouter(prefix="/progress", tags=["Progress & Adaptive Navigation"])


@router.get(
    "",
    response_model=APIResponse[OverallProgressResponse],
    summary="Get overall learner progress"
)
def get_overall_progress(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Calculate and return overall learner completion progress, milestone status, and invested time."""
    progress_data = ProgressService.get_overall_progress(
        db=db,
        user_id=current_user.id
    )
    return APIResponse(
        success=True,
        data=progress_data,
        message="Progress retrieved successfully"
    )


@router.get(
    "/skills",
    response_model=APIResponse[List[SkillProgressItem]],
    summary="Get skill-level growth and proficiency progress"
)
def get_skill_progress(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Return skill-level progress across all required skills for the learner's target role."""
    skills_data = ProgressService.get_skill_progress(
        db=db,
        user_id=current_user.id
    )
    return APIResponse(
        success=True,
        data=skills_data,
        message="Skill progress retrieved successfully"
    )


@router.get(
    "/milestones",
    response_model=APIResponse[List[MilestoneProgressItem]],
    summary="Get roadmap milestone completion breakdown"
)
def get_milestone_progress(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Return milestone-by-milestone progress for the learner's active roadmap."""
    milestones_data = ProgressService.get_milestone_progress(
        db=db,
        user_id=current_user.id
    )
    return APIResponse(
        success=True,
        data=milestones_data,
        message="Milestone progress retrieved successfully"
    )


@router.get(
    "/next-action",
    response_model=APIResponse[Optional[NextBestActionResponse]],
    summary="Get Next Best Action for learner"
)
def get_next_best_action(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Calculate and return the highest-priority, actionable next step for the learner

    based on current roadmap state, unlocked items, weak skills, and prerequisite readiness.
    """
    next_action = AdaptiveLearningService.get_next_best_action(
        db=db,
        user_id=current_user.id
    )
    return APIResponse(
        success=True,
        data=next_action,
        message="Next best action retrieved successfully" if next_action else "No pending actions found"
    )
