import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RetrievedResourceSource(BaseModel):
    """Source resource retrieved from PathFinder catalog for grounded learning context."""
    resource_id: uuid.UUID
    title: str
    description: Optional[str] = None
    url: str
    resource_type: str
    difficulty: Optional[str] = None
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    matched_skills: List[str] = Field(default_factory=list)


class RAGQueryRequest(BaseModel):
    """Direct search query request for RAG knowledge retrieval."""
    query: str = Field(..., min_length=2, max_length=1000, description="Natural language learning question")
    top_k: Optional[int] = Field(None, ge=1, le=20)
    skill_id: Optional[uuid.UUID] = Field(None, description="Optional skill filter")
    difficulty: Optional[str] = Field(None, description="Optional difficulty filter")
    resource_type: Optional[str] = Field(None, description="Optional resource type filter")


class RAGAnswerResponse(BaseModel):
    """Grounded answer generated strictly from retrieved PathFinder resources."""
    query: str
    answer: str
    sources: List[RetrievedResourceSource] = Field(default_factory=list)
    status: str = Field(..., description="GROUNDED_ANSWER | NO_RELEVANT_CONTEXT | INSUFFICIENT_CONTEXT")
