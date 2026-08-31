import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from backend.app.schemas.recommendation import ResourceSummary


class AdaptiveIntervention(BaseModel):
    """Specific learning intervention recommended by the Adaptive Learning Engine."""
    type: str = Field(..., description="refresher_resource | practice_questions | foundational_intervention | prerequisite_module | reassessment")
    skill_id: uuid.UUID
    skill_name: str
    severity: str = Field(..., description="critical | moderate | minor")
    title: str
    description: str
    recommended_action: str
    resource_id: Optional[uuid.UUID] = None
    assessment_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)


class NextBestActionResponse(BaseModel):
    """The immediate next best actionable learning step for the learner."""
    id: Optional[uuid.UUID] = Field(None, description="Roadmap item ID or intervention ID if applicable")
    skill_id: Optional[uuid.UUID] = None
    skill_name: Optional[str] = None
    action_type: str = Field(..., description="study_item | intervention | milestone | assessment")
    title: str
    reason: str
    estimated_hours: Optional[float] = None
    resource: Optional[ResourceSummary] = None
    status: str = Field("AVAILABLE", description="AVAILABLE | IN_PROGRESS | RECOMMENDED")

    model_config = ConfigDict(from_attributes=True)


class AdaptiveEvaluationRequest(BaseModel):
    """Request payload for triggering an explicit adaptive evaluation."""
    trigger_event: Optional[str] = Field("MANUAL_EVALUATION", description="Trigger signal (e.g. ASSESSMENT, ROLE_CHANGE, PROFICIENCY_UPDATE, MANUAL_EVALUATION)")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional extra evaluation context")


class AdaptiveEvaluationResponse(BaseModel):
    """Structured response detailing the adaptive engine's decisions, state changes, and next actions."""
    learner_id: uuid.UUID
    trigger_event: str
    state_changed: bool
    weak_skills_detected: List[Dict[str, Any]] = Field(default_factory=list)
    interventions: List[AdaptiveIntervention] = Field(default_factory=list)
    roadmap_updated: bool
    roadmap_id: Optional[uuid.UUID] = None
    roadmap_version: Optional[int] = None
    unlocked_items_count: int = 0
    locked_items_count: int = 0
    next_best_action: Optional[NextBestActionResponse] = None
    reason: str
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
