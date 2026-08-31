import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.services.role_service import RoleService
from backend.app.schemas.common import APIResponse
from backend.app.schemas.role import (
    RoleResponse, RoleSkillRequirementResponse, RoleDetailResponse
)

router = APIRouter(prefix="/roles", tags=["Roles Catalog"])


@router.get(
    "",
    response_model=APIResponse[List[RoleResponse]],
    summary="List career roles"
)
def list_roles(
    db: Session = Depends(get_db)
):
    """Retrieve all available career roles in the global catalog."""
    roles = RoleService.list_roles(db=db)
    return APIResponse(
        success=True,
        data=roles,
        message="Roles retrieved successfully"
    )


@router.get(
    "/{role_id}",
    response_model=APIResponse[RoleDetailResponse],
    summary="Get role details and required skills"
)
def get_role(
    role_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Retrieve career role details including all required skills, proficiency levels, and importance weights."""
    role = RoleService.get_role(db=db, role_id=role_id)
    return APIResponse(
        success=True,
        data=role,
        message="Role details retrieved successfully"
    )


@router.get(
    "/{role_id}/skills",
    response_model=APIResponse[List[RoleSkillRequirementResponse]],
    summary="Get required skills for a role"
)
def get_role_skills(
    role_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Retrieve the required skill proficiency targets for a specific career role."""
    skills = RoleService.get_role_skills(db=db, role_id=role_id)
    return APIResponse(
        success=True,
        data=skills,
        message="Role skill requirements retrieved successfully"
    )
