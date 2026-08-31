import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class RecommendationReason(BaseModel):
    skill_gap: float = Field(..., description="Skill gap relevance component score (0-1)")
    prerequisite_fit: float = Field(..., description="Prerequisite readiness component score (0-1)")
    goal_relevance: float = Field(..., description="Role goal relevance component score (0-1)")
    difficulty_fit: float = Field(..., description="Difficulty alignment component score (0-1)")
    time_fit: float = Field(..., description="Study time alignment component score (0-1)")
    preference_fit: float = Field(..., description="Learner preferences alignment component score (0-1)")
    explanation: str = Field(..., description="Human-readable explanation of why this was recommended")
    primary_skill: Optional[str] = None


class ResourceSummary(BaseModel):
    id: uuid.UUID
    title: str
    url: Optional[str] = None
    resource_type: str
    provider: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_hours: Optional[float] = None
    quality_score: Optional[float] = None
    is_free: bool = True
    skills_covered: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProjectSummary(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_hours: Optional[float] = None
    skills_covered: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RecommendationItem(BaseModel):
    id: uuid.UUID
    item_type: str = Field("resource", description="resource | project")
    resource: Optional[ResourceSummary] = None
    project: Optional[ProjectSummary] = None
    skill_id: Optional[uuid.UUID] = None
    skill_name: Optional[str] = None
    score: float = Field(..., ge=0.0, le=1.0, description="Overall recommendation score (0-1)")
    ranking: Optional[int] = None
    reason: RecommendationReason
    algorithm_version: str = "v1"
    created_at: Optional[datetime] = None


class RecommendationPagination(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class RecommendationListResponse(BaseModel):
    success: bool = True
    data: List[RecommendationItem] = []
    pagination: Optional[RecommendationPagination] = None
    message: str = "Recommendations retrieved successfully"


class RecommendationDetailResponse(BaseModel):
    success: bool = True
    data: RecommendationItem
    message: str = "Recommendation retrieved successfully"


class FeedbackCreateRequest(BaseModel):
    feedback_type: str = Field(..., description="helpful | not_helpful | too_easy | too_difficult")
    rating: Optional[int] = Field(None, ge=1, le=5, description="1 to 5 rating")
    comment: Optional[str] = Field(None, max_length=1000)


class FeedbackResponse(BaseModel):
    id: uuid.UUID
    learner_id: uuid.UUID
    resource_id: Optional[uuid.UUID] = None
    feedback_type: str
    rating: Optional[int] = None
    comment: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
