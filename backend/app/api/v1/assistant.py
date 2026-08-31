import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.api.deps import get_current_active_user
from backend.app.models.user import User
from backend.app.services.assistant_service import AssistantService
from backend.app.schemas.common import APIResponse
from backend.app.schemas.assistant import (
    AssistantChatRequest, AssistantChatData,
    ConversationSummary, ConversationDetailData
)

from backend.app.core.config import settings
from backend.app.core.security import ai_rate_limiter
from backend.app.core.exceptions import RateLimitExceededError

router = APIRouter(prefix="/assistant", tags=["AI Learning Assistant & RAG"])


@router.post(
    "/chat",
    response_model=APIResponse[AssistantChatData],
    status_code=status.HTTP_200_OK,
    summary="Send a question to the Grounded AI Learning Assistant (API_SPEC.md §15)"
)
def chat_with_assistant(
    chat_in: AssistantChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process a learner query, execute grounded RAG retrieval over curated resources,

    and return validated answers with source citations.
    """
    if settings.RATE_LIMIT_ENABLED:
        is_allowed, wait_sec = ai_rate_limiter.is_allowed(f"ai_chat:{current_user.id}")
        if not is_allowed:
            raise RateLimitExceededError(
                message=f"Too many assistant chat queries. Please try again in {wait_sec} seconds."
            )

    chat_data = AssistantService.send_message(
        db=db,
        user=current_user,
        message_text=chat_in.message,
        conversation_id=chat_in.conversation_id
    )
    return APIResponse(
        success=True,
        data=chat_data,
        message="Assistant response generated successfully"
    )


@router.get(
    "/conversations",
    response_model=APIResponse[List[ConversationSummary]],
    status_code=status.HTTP_200_OK,
    summary="List authenticated learner's assistant conversations (API_SPEC.md §15)"
)
def list_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Return paginated list of conversations belonging to the authenticated learner."""
    conversations, total = AssistantService.list_conversations(
        db=db,
        user=current_user,
        page=page,
        page_size=page_size
    )
    return APIResponse(
        success=True,
        data=conversations,
        message="Conversations retrieved successfully"
    )


@router.get(
    "/conversations/{id}",
    response_model=APIResponse[ConversationDetailData],
    status_code=status.HTTP_200_OK,
    summary="Get full conversation history by ID (API_SPEC.md §15)"
)
def get_conversation(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Return single conversation and its chronological messages. Strictly user-isolated."""
    conv_detail = AssistantService.get_conversation(
        db=db,
        user=current_user,
        conversation_id=id
    )
    return APIResponse(
        success=True,
        data=conv_detail,
        message="Conversation retrieved successfully"
    )
