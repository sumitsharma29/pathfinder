import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.learner_profile import LearnerProfile
    from backend.app.models.roadmap_item import RoadmapItem


class Progress(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "progress"

    learner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learner_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    roadmap_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roadmap_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, server_default="0.0", nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    time_spent_minutes: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)

    # Relationships
    learner: Mapped["LearnerProfile"] = relationship("LearnerProfile", back_populates="progress_records")
    roadmap_item: Mapped["RoadmapItem"] = relationship("RoadmapItem", back_populates="progress_records")

    __table_args__ = (
        Index("idx_progress_learner_id", "learner_id"),
        Index("idx_progress_roadmap_item_id", "roadmap_item_id"),
        CheckConstraint("percentage >= 0 AND percentage <= 100", name="chk_progress_percentage"),
        CheckConstraint("time_spent_minutes >= 0", name="chk_progress_time_spent"),
    )
