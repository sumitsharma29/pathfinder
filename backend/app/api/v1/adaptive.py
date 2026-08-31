from typing import Optional
from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.api.deps import get_current_active_user
from backend.app.models.user import User
from backend.app.services.adaptive_learning_service import AdaptiveLearningService
from backend.app.schemas.common import APIResponse
from backend.app.schemas.adaptive import (
    AdaptiveEvaluationRequest, AdaptiveEvaluationResponse
)

router = APIRouter(prefix="/adaptation", tags=["Adaptive Learning Engine"])


@router.post(
    "/evaluate",
    response_model=APIResponse[AdaptiveEvaluationResponse],
    summary="Evaluate learner state and trigger adaptive learning loop"
)
def evaluate_adaptation(
    eval_in: Optional[AdaptiveEvaluationRequest] = Body(default=None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Trigger the deterministic Adaptive Learning Engine to detect weak skills,

    select interventions, re-evaluate roadmap prerequisites, and determine the next best action.
    """
    trigger_event = eval_in.trigger_event if eval_in and eval_in.trigger_event else "MANUAL_EVALUATION"
    context = eval_in.context if eval_in and eval_in.context else {}

    result = AdaptiveLearningService.evaluate_and_adapt(
        db=db,
        user_id=current_user.id,
        trigger_event=trigger_event,
        context=context
    )
    return APIResponse(
        success=True,
        data=result,
        message="Adaptive evaluation completed successfully"
    )
