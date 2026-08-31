import uuid
from typing import List
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.api.deps import get_current_active_user
from backend.app.models.user import User
from backend.app.services.learner_profile_service import LearnerProfileService
from backend.app.schemas.common import APIResponse
from backend.app.schemas.profile import (
    LearnerProfileResponse, LearnerProfileUpdateRequest,
    LearnerSkillCreateRequest, LearnerSkillUpdateRequest,
    LearnerSkillItemResponse, TargetRoleSummary
)

router = APIRouter(prefix="/profile", tags=["Learner Profile"])


@router.get(
    "",
    response_model=APIResponse[LearnerProfileResponse],
    summary="Get current learner profile"
)
def get_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Return the authenticated learner's profile, including target career role and preferences."""
    profile = LearnerProfileService.get_profile(db=db, user_id=current_user.id)
    
    role_summary = None
    if profile.target_role:
        role_summary = TargetRoleSummary(
            id=profile.target_role.id,
            name=profile.target_role.name,
            slug=profile.target_role.slug
        )

    profile_data = LearnerProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        target_role=role_summary,
        experience_level=profile.experience_level,
        daily_study_hours=float(profile.daily_study_hours) if profile.daily_study_hours is not None else None,
        target_duration_weeks=profile.target_duration_weeks,
        learning_preferences=profile.learning_preferences or {}
    )

    return APIResponse(
        success=True,
        data=profile_data,
        message="Profile retrieved successfully"
    )


@router.put(
    "",
    response_model=APIResponse[LearnerProfileResponse],
    summary="Update learner profile"
)
def update_profile(
    update_in: LearnerProfileUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update target career role, experience level, daily study hours, or learning preferences."""
    updated = LearnerProfileService.update_profile(
        db=db,
        user_id=current_user.id,
        update_in=update_in
    )

    role_summary = None
    if updated.target_role:
        role_summary = TargetRoleSummary(
            id=updated.target_role.id,
            name=updated.target_role.name,
            slug=updated.target_role.slug
        )

    profile_data = LearnerProfileResponse(
        id=updated.id,
        user_id=updated.user_id,
        target_role=role_summary,
        experience_level=updated.experience_level,
        daily_study_hours=float(updated.daily_study_hours) if updated.daily_study_hours is not None else None,
        target_duration_weeks=updated.target_duration_weeks,
        learning_preferences=updated.learning_preferences or {}
    )

    return APIResponse(
        success=True,
        data=profile_data,
        message="Profile updated successfully"
    )


@router.get(
    "/skills",
    response_model=APIResponse[List[LearnerSkillItemResponse]],
    summary="Get learner's current skills"
)
def get_learner_skills(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Return all skills declared or acquired by the authenticated learner."""
    skills = LearnerProfileService.get_learner_skills(db=db, user_id=current_user.id)
    return APIResponse(
        success=True,
        data=skills,
        message="Skills retrieved successfully"
    )


@router.post(
    "/skills",
    response_model=APIResponse[LearnerSkillItemResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add a skill to learner profile"
)
def add_learner_skill(
    skill_in: LearnerSkillCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a self-declared or assessment-verified skill with proficiency (0-100)."""
    added = LearnerProfileService.add_learner_skill(
        db=db,
        user_id=current_user.id,
        skill_in=skill_in
    )
    return APIResponse(
        success=True,
        data=added,
        message="Skill added to profile successfully"
    )


@router.put(
    "/skills/{skill_id}",
    response_model=APIResponse[LearnerSkillItemResponse],
    summary="Update skill proficiency"
)
def update_learner_skill(
    skill_id: uuid.UUID,
    update_in: LearnerSkillUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update the proficiency rating of an existing skill in the learner's profile."""
    updated = LearnerProfileService.update_learner_skill(
        db=db,
        user_id=current_user.id,
        skill_id=skill_id,
        update_in=update_in
    )
    return APIResponse(
        success=True,
        data=updated,
        message="Skill proficiency updated successfully"
    )


@router.delete(
    "/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a skill from learner profile"
)
def delete_learner_skill(
    skill_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove a skill entry from the authenticated learner's profile."""
    LearnerProfileService.delete_learner_skill(
        db=db,
        user_id=current_user.id,
        skill_id=skill_id
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
