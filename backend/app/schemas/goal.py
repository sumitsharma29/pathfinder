import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class GoalAnalysisRequest(BaseModel):
    """Request schema for analyzing an unstructured natural-language career goal (API_SPEC.md §8)."""
    text: Optional[str] = Field(
        None,
        description="Natural language career or learning goal description (API_SPEC.md §8)"
    )
    goal_text: Optional[str] = Field(
        None,
        description="Alternative field name for natural language career goal"
    )

    @property
    def raw_text(self) -> str:
        val = self.text or self.goal_text or ""
        return val.strip()

    @field_validator("text", "goal_text")
    @classmethod
    def validate_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.strip()
            if len(clean) > 2000:
                raise ValueError("Goal text exceeds maximum length of 2000 characters.")
        return v

    def model_post_init(self, __context: Any) -> None:
        raw = self.raw_text
        if len(raw) < 3:
            raise ValueError("Goal text must be at least 3 characters long and non-empty.")


class LLMGoalExtractionCandidate(BaseModel):
    """Raw structured candidate returned by the LLM before server-side grounding and validation."""
    target_role: Optional[str] = Field(None, description="Extracted career target role title")
    timeline_weeks: Optional[int] = Field(None, description="Timeline in weeks")
    daily_study_hours: Optional[float] = Field(None, description="Daily available study hours")
    experience_level: Optional[str] = Field(None, description="beginner, intermediate, advanced, or null")
    technologies: List[str] = Field(default_factory=list, description="Extracted technologies and tools")
    known_skills: List[str] = Field(default_factory=list, description="Skills the user claims to know or mention")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="Learning preferences and constraints")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Model extraction confidence")
    missing_information: List[str] = Field(default_factory=list, description="List of missing crucial parameters")


class ExtractedSkillItem(BaseModel):
    """Grounded skill representation mapped to canonical database catalog."""
    name: str = Field(..., description="Original extracted skill name")
    matched_name: Optional[str] = Field(None, description="Canonical catalog skill name")
    skill_id: Optional[uuid.UUID] = Field(None, description="Database skill UUID if grounded")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Skill grounding confidence")
    status: str = Field(..., description="CONFIRMED | INFERRED | UNRESOLVED")


class SuggestedRoleItem(BaseModel):
    """Alternative role option presented when input goal is ambiguous."""
    id: uuid.UUID
    name: str
    slug: str
    match_score: float


class GoalAnalysisData(BaseModel):
    """Validated, normalized, and grounded structured goal output."""
    raw_goal: str
    target_role: Optional[str] = None
    role_id: Optional[uuid.UUID] = None
    role_slug: Optional[str] = None
    role_confidence: float = Field(0.0, ge=0.0, le=1.0)
    timeline_weeks: Optional[int] = None
    daily_study_hours: Optional[float] = None
    experience_level: Optional[str] = None
    known_skills: List[ExtractedSkillItem] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(..., ge=0.0, le=1.0)
    status: str = Field(..., description="RESOLVED | AMBIGUOUS | UNRESOLVED | CLARIFICATION_REQUIRED")
    missing_information: List[str] = Field(default_factory=list)
    clarification_prompt: Optional[str] = None
    suggested_roles: List[SuggestedRoleItem] = Field(default_factory=list)
