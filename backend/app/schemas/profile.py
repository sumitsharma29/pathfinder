import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class TargetRoleSummary(BaseModel):
    id: uuid.UUID
    name: str
    slug: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LearnerProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    target_role: Optional[TargetRoleSummary] = None
    experience_level: Optional[str] = None
    daily_study_hours: Optional[float] = None
    target_duration_weeks: Optional[int] = None
    learning_preferences: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class LearnerProfileUpdateRequest(BaseModel):
    target_role_id: Optional[uuid.UUID] = None
    experience_level: Optional[str] = Field(None, description="Experience level: beginner, intermediate, advanced, not_sure")
    daily_study_hours: Optional[float] = Field(None, ge=0.0, le=24.0, description="Daily available study hours (>= 0)")
    target_duration_weeks: Optional[int] = Field(None, gt=0, le=200, description="Target completion timeline in weeks (> 0)")
    learning_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Learning style and content preferences")


class LearnerSkillItemResponse(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    skill_slug: Optional[str] = None
    category: Optional[str] = None
    proficiency: float = Field(..., ge=0.0, le=100.0)
    source: str = "self_declared"
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class LearnerSkillCreateRequest(BaseModel):
    skill_id: uuid.UUID
    proficiency: float = Field(..., ge=0.0, le=100.0, description="Skill proficiency from 0 to 100")
    source: str = Field("self_declared", description="Source: self_declared, assessment, imported, inferred")
    confidence: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")


class LearnerSkillUpdateRequest(BaseModel):
    proficiency: float = Field(..., ge=0.0, le=100.0, description="Skill proficiency from 0 to 100")
    source: Optional[str] = Field(None, description="Source of update")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
