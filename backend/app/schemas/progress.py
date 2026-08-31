import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from backend.app.schemas.adaptive import NextBestActionResponse, AdaptiveIntervention
from backend.app.schemas.recommendation import RecommendationItem


class MilestoneSummary(BaseModel):
    roadmap_item_id: uuid.UUID
    title: str
    status: str
    sequence_order: int
    estimated_minutes: int
    skill_id: uuid.UUID
    skill_name: str


class OverallProgressResponse(BaseModel):
    """Overall learner progress metrics derived dynamically from activity."""
    overall_percentage: float = Field(..., description="Percentage of roadmap milestones completed (0.0 - 100.0)")
    completed_items: int = Field(..., description="Total completed roadmap milestone items")
    total_items: int = Field(..., description="Total milestone items in the active roadmap")
    time_spent_minutes: int = Field(..., description="Estimated or actual total minutes invested")
    active_roadmap_id: Optional[uuid.UUID] = Field(None, description="Current active roadmap ID")
    current_milestone: Optional[MilestoneSummary] = Field(None, description="Currently in-progress or earliest available milestone")


class SkillProgressItem(BaseModel):
    """Skill proficiency and gap progress for a learner towards their target role."""
    skill_id: uuid.UUID
    skill: str
    category: Optional[str] = None
    current_proficiency: float
    required_proficiency: float
    gap: float
    status: str = Field(..., description="MASTERED | PARTIAL | MISSING")
    importance: float


class MilestoneProgressItem(BaseModel):
    """Detailed milestone progress item in active roadmap."""
    roadmap_item_id: uuid.UUID
    title: str
    status: str = Field(..., description="LOCKED | AVAILABLE | IN_PROGRESS | COMPLETED | SKIPPED")
    percentage: float = Field(..., description="Milestone completion percentage (0.0 or 100.0)")
    sequence_order: int
    estimated_minutes: int
    skill_id: uuid.UUID
    skill_name: str
    resource_id: Optional[uuid.UUID] = None
    resource_title: Optional[str] = None


class DashboardOverview(BaseModel):
    target_role_id: Optional[uuid.UUID] = None
    target_role_title: Optional[str] = None
    readiness_score: float = Field(..., description="Overall role readiness score percentage")
    overall_progress_percentage: float
    active_roadmap_id: Optional[uuid.UUID] = None
    roadmap_version: int = 1


class DashboardCompletedMetrics(BaseModel):
    completed_milestones_count: int
    mastered_skills_count: int
    total_skills_count: int
    completed_assessments_count: int
    total_time_spent_minutes: int


class DashboardWeakAreas(BaseModel):
    weak_skills: List[str]
    critical_skill_gaps: int
    interventions_needed: List[AdaptiveIntervention]


class DashboardLearningFocus(BaseModel):
    current_milestone: Optional[MilestoneSummary] = None
    active_recommendations: List[RecommendationItem] = []


class DashboardAggregationResponse(BaseModel):
    """Unified 5-question dashboard aggregation for the learner."""
    overview: DashboardOverview
    completed_metrics: DashboardCompletedMetrics
    weak_areas: DashboardWeakAreas
    learning_focus: DashboardLearningFocus
    next_best_action: Optional[NextBestActionResponse] = None
