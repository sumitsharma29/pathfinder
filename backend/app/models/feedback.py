import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Index, CheckConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.models.learner_profile import LearnerProfile
    from backend.app.models.resource import Resource


class Feedback(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "feedback"

    learner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learner_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resources.id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )
    feedback_type: Mapped[str] = mapped_column(String(50), nullable=False)  # helpful, not_helpful, too_easy, too_difficult, etc.
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )

    # Relationships
    learner: Mapped["LearnerProfile"] = relationship("LearnerProfile", back_populates="feedbacks")
    resource: Mapped[Optional["Resource"]] = relationship("Resource", back_populates="feedbacks")

    __table_args__ = (
        Index("idx_feedback_learner_id", "learner_id"),
        Index("idx_feedback_resource_id", "resource_id"),
        CheckConstraint("rating IS NULL OR (rating >= 1 AND rating <= 5)", name="chk_feedback_rating"),
    )
