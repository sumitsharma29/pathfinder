import uuid
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RoleSkillRequirementResponse(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    skill_slug: str
    category: str
    difficulty: Optional[str] = None
    required_proficiency: float
    importance: float


class RoleDetailResponse(RoleResponse):
    required_skills: List[RoleSkillRequirementResponse] = []
