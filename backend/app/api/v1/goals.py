from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.api.deps import get_current_active_user
from backend.app.models.user import User
from backend.app.services.goal_service import GoalService
from backend.app.schemas.common import APIResponse
from backend.app.schemas.goal import GoalAnalysisRequest, GoalAnalysisData

from backend.app.core.config import settings
from backend.app.core.security import ai_rate_limiter
from backend.app.core.exceptions import RateLimitExceededError

router = APIRouter(tags=["AI Goal Understanding"])


@router.post(
    "/ai/analyze-goal",
    response_model=APIResponse[GoalAnalysisData],
    status_code=status.HTTP_200_OK,
    summary="Analyze a natural-language career goal (API_SPEC.md §8)"
)
def analyze_goal(
    goal_in: GoalAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analyze a natural-language learning goal, extract structured candidates,

    and ground them deterministically against active career role and skill catalogs.
    """
    if settings.RATE_LIMIT_ENABLED:
        is_allowed, wait_sec = ai_rate_limiter.is_allowed(f"ai_goal:{current_user.id}")
        if not is_allowed:
            raise RateLimitExceededError(
                message=f"Too many goal analysis requests. Please try again in {wait_sec} seconds."
            )

    analysis_data = GoalService.analyze_goal(
        db=db,
        goal_text=goal_in.raw_text
    )
    return APIResponse(
        success=True,
        data=analysis_data,
        message="Goal analyzed and grounded successfully"
    )
