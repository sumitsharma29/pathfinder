import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.api.deps import get_current_active_user
from backend.app.models.user import User
from backend.app.services.skill_gap_service import SkillGapService
from backend.app.schemas.skill_gap import SkillGapResponse

router = APIRouter(prefix="/skill-gaps", tags=["Skill Gaps Engine"])


class AnalyzeSkillGapsRequest(BaseModel):
    role_id: Optional[uuid.UUID] = None


@router.get(
    "",
    response_model=SkillGapResponse,
    summary="Get current skill gaps against target role"
)
def get_skill_gaps(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Dynamically compute skill gaps for the authenticated learner against their selected target role."""
    data = SkillGapService.analyze_gaps(
        db=db,
        user_id=current_user.id
    )
    return SkillGapResponse(
        success=True,
        data=data,
        message="Skill gap analysis completed"
    )


@router.post(
    "/analyze",
    response_model=SkillGapResponse,
    summary="Trigger dynamic skill gap calculation"
)
def analyze_skill_gaps(
    req: Optional[AnalyzeSkillGapsRequest] = Body(default=None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Trigger real-time dynamic skill gap calculation for the authenticated learner (optionally specifying an override target role)."""
    override_role_id = req.role_id if req else None
    data = SkillGapService.analyze_gaps(
        db=db,
        user_id=current_user.id,
        override_role_id=override_role_id
    )
    return SkillGapResponse(
        success=True,
        data=data,
        message="Skill gap analysis completed"
    )
