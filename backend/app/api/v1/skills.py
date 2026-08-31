import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.services.skill_service import SkillService
from backend.app.schemas.common import APIResponse
from backend.app.schemas.skill import (
    SkillResponse, SkillPrerequisiteResponse, SkillDetailResponse
)

router = APIRouter(prefix="/skills", tags=["Skills Catalog"])


@router.get(
    "",
    response_model=APIResponse[List[SkillResponse]],
    summary="List all catalog skills"
)
def list_skills(
    category: Optional[str] = Query(None, description="Filter skills by category"),
    db: Session = Depends(get_db)
):
    """Retrieve the global skill catalog with optional category filtering."""
    skills = SkillService.list_skills(db=db, category=category)
    return APIResponse(
        success=True,
        data=skills,
        message="Skills retrieved successfully"
    )


@router.get(
    "/{skill_id}",
    response_model=APIResponse[SkillDetailResponse],
    summary="Get skill details and dependencies"
)
def get_skill(
    skill_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Retrieve detailed metadata and prerequisite dependencies for a skill."""
    skill = SkillService.get_skill(db=db, skill_id=skill_id)
    return APIResponse(
        success=True,
        data=skill,
        message="Skill details retrieved successfully"
    )


@router.get(
    "/{skill_id}/prerequisites",
    response_model=APIResponse[List[SkillPrerequisiteResponse]],
    summary="Get prerequisite skills for a skill"
)
def get_skill_prerequisites(
    skill_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Retrieve the direct upstream prerequisites required before learning this skill."""
    prereqs = SkillService.get_prerequisites(db=db, skill_id=skill_id)
    return APIResponse(
        success=True,
        data=prereqs,
        message="Prerequisites retrieved successfully"
    )
