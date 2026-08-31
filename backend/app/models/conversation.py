import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.learner_profile import LearnerProfile
    from backend.app.models.conversation_message import ConversationMessage


class Conversation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "conversations"

    learner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learner_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    learner: Mapped["LearnerProfile"] = relationship("LearnerProfile", back_populates="conversations")
    messages: Mapped[List["ConversationMessage"]] = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ConversationMessage.created_at"
    )

    __table_args__ = (
        Index("idx_conversations_learner_id", "learner_id"),
    )
