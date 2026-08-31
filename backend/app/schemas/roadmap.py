import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from backend.app.schemas.recommendation import ResourceSummary, ProjectSummary


class SkillSummary(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    category: str

    model_config = ConfigDict(from_attributes=True)


class RoadmapItemReason(BaseModel):
    skill_gap: Optional[float] = None
    importance: Optional[float] = None
    prerequisites: List[str] = Field(default_factory=list)
    explanation: str = Field(..., description="Human-readable reason for sequence placement")


class RoadmapItemResponse(BaseModel):
    id: uuid.UUID
    roadmap_id: uuid.UUID
    sequence: int
    skill: Optional[SkillSummary] = None
    resource: Optional[ResourceSummary] = None
    project: Optional[ProjectSummary] = None
    assessment: Optional[Dict[str, Any]] = None
    status: str = Field(..., description="LOCKED | AVAILABLE | IN_PROGRESS | COMPLETED")
    progress: float = Field(0.0, ge=0.0, le=100.0)
    estimated_hours: Optional[float] = None
    reason: Optional[Dict[str, Any]] = None
    locked_reason: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RoadmapGenerateRequest(BaseModel):
    target_role_id: Optional[uuid.UUID] = None
    target_duration_weeks: Optional[int] = Field(None, gt=0, le=200)


class RoadmapResponse(BaseModel):
    id: uuid.UUID
    target_role_id: uuid.UUID
    target_role_name: Optional[str] = None
    version: int
    status: str
    estimated_weeks: Optional[int] = None
    items: List[RoadmapItemResponse] = Field(default_factory=list)
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RoadmapSummaryResponse(BaseModel):
    roadmap_id: uuid.UUID
    version: int
    status: str
    estimated_weeks: Optional[int] = None
    total_items: int
    completed_items: int
    in_progress_items: int
    available_items: int
    locked_items: int
    overall_progress: float
    next_best_action: Optional[RoadmapItemResponse] = None
    items: List[RoadmapItemResponse] = Field(default_factory=list)
