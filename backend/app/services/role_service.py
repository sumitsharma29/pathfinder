import uuid
from typing import List
from sqlalchemy.orm import Session
from backend.app.core.exceptions import NotFoundError
from backend.app.repositories.role_repository import RoleRepository
from backend.app.schemas.role import RoleResponse, RoleSkillRequirementResponse, RoleDetailResponse
from backend.app.models.role import Role


class RoleService:
    """Service handling read-only role catalog and role skill requirements."""

    @staticmethod
    def list_roles(db: Session) -> List[RoleResponse]:
        """List all career roles in catalog."""
        roles = RoleRepository.get_all(db)
        return [
            RoleResponse(
                id=r.id,
                name=r.name,
                slug=r.slug,
                description=r.description
            )
            for r in roles
        ]

    @staticmethod
    def get_role(db: Session, role_id: uuid.UUID) -> RoleDetailResponse:
        """Get role details with required skills."""
        role = RoleRepository.get_by_id(db, role_id)
        if not role:
            raise NotFoundError(message="Role not found", details={"role_id": str(role_id)})

        role_skills = RoleRepository.get_role_skills(db, role_id)
        reqs = [
            RoleSkillRequirementResponse(
                skill_id=rs.skill_id,
                skill_name=rs.skill.name if rs.skill else "",
                skill_slug=rs.skill.slug if rs.skill else "",
                category=rs.skill.category if rs.skill else "",
                difficulty=rs.skill.difficulty if rs.skill else None,
                required_proficiency=float(rs.required_proficiency),
                importance=float(rs.importance)
            )
            for rs in role_skills
        ]

        return RoleDetailResponse(
            id=role.id,
            name=role.name,
            slug=role.slug,
            description=role.description,
            required_skills=reqs
        )

    @staticmethod
    def get_role_skills(db: Session, role_id: uuid.UUID) -> List[RoleSkillRequirementResponse]:
        """Fetch required skills for a role."""
        role = RoleRepository.get_by_id(db, role_id)
        if not role:
            raise NotFoundError(message="Role not found", details={"role_id": str(role_id)})

        role_skills = RoleRepository.get_role_skills(db, role_id)
        return [
            RoleSkillRequirementResponse(
                skill_id=rs.skill_id,
                skill_name=rs.skill.name if rs.skill else "",
                skill_slug=rs.skill.slug if rs.skill else "",
                category=rs.skill.category if rs.skill else "",
                difficulty=rs.skill.difficulty if rs.skill else None,
                required_proficiency=float(rs.required_proficiency),
                importance=float(rs.importance)
            )
            for rs in role_skills
        ]
