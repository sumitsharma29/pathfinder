import uuid
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc

from backend.app.models.user import User
from backend.app.models.learner_profile import LearnerProfile
from backend.app.models.conversation import Conversation
from backend.app.models.conversation_message import ConversationMessage
from backend.app.services.rag_service import RAGService
from backend.app.schemas.assistant import (
    AssistantChatData, AssistantMessageItem,
    ConversationSummary, ConversationDetailData
)
from backend.app.schemas.rag import RetrievedResourceSource
from backend.app.core.exceptions import AppException


class AssistantService:
    """Learning Assistant Service orchestrating user conversations and grounded RAG responses."""

    @classmethod
    def send_message(
        cls,
        db: Session,
        user: User,
        message_text: str,
        conversation_id: Optional[uuid.UUID] = None
    ) -> AssistantChatData:
        """Process a learner query, perform grounded RAG retrieval, and record conversation messages."""
        profile: Optional[LearnerProfile] = user.profile
        if not profile:
            raise AppException(status_code=400, code="PROFILE_REQUIRED", message="Learner profile does not exist.")

        # 1. Resolve or create conversation
        if conversation_id:
            conv = db.execute(
                select(Conversation)
                .where(Conversation.id == conversation_id, Conversation.learner_id == profile.id)
            ).scalar_one_or_none()

            if not conv:
                # Check if conversation exists under another learner for 403 authorization safety
                other_conv = db.execute(
                    select(Conversation).where(Conversation.id == conversation_id)
                ).scalar_one_or_none()
                if other_conv:
                    raise AppException(status_code=403, code="FORBIDDEN", message="You do not have access to this conversation.")
                raise AppException(status_code=404, code="CONVERSATION_NOT_FOUND", message="Conversation not found.")
        else:
            title_snippet = message_text.strip().split("\n")[0][:80]
            conv = Conversation(
                learner_id=profile.id,
                title=title_snippet
            )
            db.add(conv)
            db.flush()

        # 2. Record User Message
        user_msg = ConversationMessage(
            conversation_id=conv.id,
            role="user",
            content=message_text.strip(),
            meta_data={}
        )
        db.add(user_msg)
        db.flush()

        # 3. Assemble dynamic learner context
        learner_context = {}
        if profile.target_role:
            learner_context["target_role"] = getattr(profile.target_role, "title", None) or profile.target_role.name

        if profile.target_role_id:
            try:
                from backend.app.services.skill_gap_service import SkillGapService
                from backend.app.services.adaptive_learning_service import AdaptiveLearningService
                
                gap_summary = SkillGapService.calculate_gaps(db, profile.id, profile.target_role_id)
                weak_skills = [g.skill_name for g in gap_summary.gaps if g.status in ["MISSING", "PARTIAL"]]
                if weak_skills:
                    learner_context["weak_skills"] = weak_skills[:3]
                if gap_summary.gaps:
                    highest_gap = max(gap_summary.gaps, key=lambda g: g.gap * g.importance)
                    learner_context["highest_priority_gap"] = f"{highest_gap.skill_name} (Gap: {highest_gap.gap}%)"
                
                next_action = AdaptiveLearningService.get_next_best_action(db, user.id)
                if next_action:
                    learner_context["next_best_action"] = f"{next_action.action_type}: {next_action.title}"
            except Exception:
                pass

        if hasattr(profile, "weekly_goal_hours") and profile.weekly_goal_hours:
            learner_context["weekly_study_hours"] = profile.weekly_goal_hours

        # 4. Generate Grounded Answer via RAGService
        rag_result = RAGService.generate_grounded_answer(
            db=db,
            query=message_text,
            learner_context=learner_context,
            target_role_id=profile.target_role_id
        )

        # 5. Record Assistant Message
        sources_meta = [s.model_dump(mode="json") for s in rag_result.sources]
        asst_msg = ConversationMessage(
            conversation_id=conv.id,
            role="assistant",
            content=rag_result.answer,
            meta_data={"sources": sources_meta, "status": rag_result.status}
        )
        db.add(asst_msg)
        db.commit()
        db.refresh(asst_msg)

        message_item = AssistantMessageItem(
            id=asst_msg.id,
            role="assistant",
            content=asst_msg.content,
            created_at=asst_msg.created_at,
            sources=rag_result.sources
        )

        return AssistantChatData(
            conversation_id=conv.id,
            message=message_item,
            sources=rag_result.sources
        )

    @classmethod
    def list_conversations(
        cls,
        db: Session,
        user: User,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ConversationSummary], int]:
        """List authenticated learner's conversations with pagination."""
        profile = user.profile
        if not profile:
            return [], 0

        offset = (page - 1) * page_size
        total = db.scalar(
            select(func.count(Conversation.id)).where(Conversation.learner_id == profile.id)
        ) or 0

        stmt = (
            select(Conversation)
            .where(Conversation.learner_id == profile.id)
            .order_by(desc(Conversation.updated_at))
            .offset(offset)
            .limit(page_size)
        )
        conversations = db.execute(stmt).scalars().all()

        summaries = []
        for c in conversations:
            msg_count = db.scalar(
                select(func.count(ConversationMessage.id)).where(ConversationMessage.conversation_id == c.id)
            ) or 0
            summaries.append(
                ConversationSummary(
                    id=c.id,
                    title=c.title,
                    message_count=msg_count,
                    created_at=c.created_at,
                    updated_at=c.updated_at
                )
            )

        return summaries, total

    @classmethod
    def get_conversation(
        cls,
        db: Session,
        user: User,
        conversation_id: uuid.UUID
    ) -> ConversationDetailData:
        """Get full conversation details and chronological message history."""
        profile = user.profile
        if not profile:
            raise AppException(status_code=400, code="PROFILE_REQUIRED", message="Learner profile does not exist.")

        conv = db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        ).scalar_one_or_none()

        if not conv:
            raise AppException(status_code=404, code="CONVERSATION_NOT_FOUND", message="Conversation not found.")

        if conv.learner_id != profile.id:
            raise AppException(status_code=403, code="FORBIDDEN", message="You do not have access to this conversation.")

        messages_rows = db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conv.id)
            .order_by(ConversationMessage.created_at.asc())
        ).scalars().all()

        message_items = []
        for m in messages_rows:
            raw_sources = m.meta_data.get("sources", []) if isinstance(m.meta_data, dict) else []
            sources_objs = []
            for s in raw_sources:
                try:
                    sources_objs.append(RetrievedResourceSource.model_validate(s))
                except Exception:
                    pass

            message_items.append(
                AssistantMessageItem(
                    id=m.id,
                    role=m.role,
                    content=m.content,
                    created_at=m.created_at,
                    sources=sources_objs
                )
            )

        return ConversationDetailData(
            id=conv.id,
            title=conv.title,
            messages=message_items,
            created_at=conv.created_at,
            updated_at=conv.updated_at
        )
