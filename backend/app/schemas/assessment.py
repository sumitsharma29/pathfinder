import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from backend.app.schemas.roadmap import SkillSummary


class AssessmentQuestionPublic(BaseModel):
    """Public representation of an assessment question without answers."""
    id: uuid.UUID
    question: str
    question_type: str
    options: Optional[Dict[str, Any]] = None
    points: float

    model_config = {"from_attributes": True}


class AssessmentSummary(BaseModel):
    """Summary of an assessment in catalog."""
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    difficulty: Optional[str] = "intermediate"
    passing_score: float
    skill: Optional[SkillSummary] = None
    question_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AssessmentDetailResponse(BaseModel):
    """Detailed assessment response including questions for taking the test."""
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    difficulty: Optional[str] = "intermediate"
    passing_score: float
    skill: Optional[SkillSummary] = None
    questions: List[AssessmentQuestionPublic]
    created_at: datetime

    model_config = {"from_attributes": True}


class AnswerSubmissionItem(BaseModel):
    """A single submitted answer for a question."""
    question_id: uuid.UUID
    answer: str = Field(..., min_length=1, max_length=1000)


class AssessmentSubmissionRequest(BaseModel):
    """Assessment submission payload containing learner answers."""
    answers: List[AnswerSubmissionItem] = Field(..., min_length=1)


class AssessmentResultResponse(BaseModel):
    """Response returned after scoring an assessment submission."""
    id: uuid.UUID
    assessment_id: uuid.UUID
    assessment_title: str
    skill_id: uuid.UUID
    skill_name: str
    attempt_number: int
    score: float
    skill_mastery: float
    passed: bool
    total_questions: int
    correct_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AssessmentHistoryItem(BaseModel):
    """Item in learner assessment history."""
    id: uuid.UUID
    assessment_id: uuid.UUID
    assessment_title: str
    skill_name: str
    attempt_number: int
    score: float
    skill_mastery: float
    passed: bool
    created_at: datetime

    model_config = {"from_attributes": True}
