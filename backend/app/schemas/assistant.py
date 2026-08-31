import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from backend.app.schemas.rag import RetrievedResourceSource


class AssistantChatRequest(BaseModel):
    """Request schema for sending a message to PathFinder AI Assistant (API_SPEC.md §15)."""
    conversation_id: Optional[uuid.UUID] = Field(None, description="Existing conversation UUID or null for new")
    message: str = Field(..., min_length=1, max_length=2000, description="User question or learning query")


class AssistantMessageItem(BaseModel):
    """Public representation of a single conversation message."""
    id: uuid.UUID
    role: str = Field(..., description="user | assistant | system")
    content: str
    created_at: datetime
    sources: List[RetrievedResourceSource] = Field(default_factory=list)


class AssistantChatData(BaseModel):
    """Response data structure for assistant chat interactions (API_SPEC.md §15)."""
    conversation_id: uuid.UUID
    message: AssistantMessageItem
    sources: List[RetrievedResourceSource] = Field(default_factory=list)


class ConversationSummary(BaseModel):
    """Summary item for listing learner assistant conversations."""
    id: uuid.UUID
    title: Optional[str] = None
    message_count: int
    created_at: datetime
    updated_at: datetime


class ConversationDetailData(BaseModel):
    """Detailed conversation view containing all chronological messages."""
    id: uuid.UUID
    title: Optional[str] = None
    messages: List[AssistantMessageItem] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
