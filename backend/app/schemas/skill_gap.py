import uuid
from typing import List, Optional
from pydantic import BaseModel, Field


class SkillGapItem(BaseModel):
    skill_id: uuid.UUID
    skill: str
    skill_slug: str
    category: str
    required: float = Field(..., description="Target proficiency required for the role (0-100)")
    current: float = Field(..., description="Learner's current proficiency (0-100)")
    gap: float = Field(..., description="Calculated gap: max(required - current, 0)")
    importance: float = Field(..., description="Role importance weight (0-1)")
    priority: float = Field(..., description="Calculated priority score")
    status: str = Field(..., description="MASTERED | PARTIAL | MISSING")
    prerequisites: List[str] = Field(default_factory=list, description="List of prerequisite skill names")


class SkillGapSummary(BaseModel):
    total_skills_required: int
    skills_mastered: int
    skills_in_progress: int
    skills_missing: int
    average_gap: float
    overall_readiness_percentage: float


class SkillGapAnalysisData(BaseModel):
    target_role_id: uuid.UUID
    target_role: str
    summary: SkillGapSummary
    skills: List[SkillGapItem]


class SkillGapResponse(BaseModel):
    success: bool = True
    data: SkillGapAnalysisData
    message: str = "Skill gap analysis completed"
