import uuid
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class SkillResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    category: str
    description: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_hours: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class SkillPrerequisiteResponse(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    prerequisite_skill_id: uuid.UUID
    prerequisite_skill_name: str
    prerequisite_skill_slug: str
    strength: float


class SkillDetailResponse(SkillResponse):
    prerequisites: List[SkillPrerequisiteResponse] = []
    dependent_skills: List[SkillPrerequisiteResponse] = []
