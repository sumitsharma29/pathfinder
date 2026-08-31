import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, Index, CheckConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, JSONB

if TYPE_CHECKING:
    from backend.app.models.learner_profile import LearnerProfile
    from backend.app.models.skill import Skill
    from backend.app.models.resource import Resource


class Recommendation(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "recommendations"

    learner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learner_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    skill_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="RESTRICT"),
        nullable=True
    )
    resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resources.id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )
    score: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    ranking: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reason: Mapped[dict] = mapped_column(JSONB, nullable=False)
    algorithm_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )

    # Relationships
    learner: Mapped["LearnerProfile"] = relationship("LearnerProfile", back_populates="recommendations")
    skill: Mapped[Optional["Skill"]] = relationship("Skill", back_populates="recommendations")
    resource: Mapped[Optional["Resource"]] = relationship("Resource", back_populates="recommendations")

    __table_args__ = (
        Index("idx_recommendations_learner_id", "learner_id"),
        Index("idx_recommendations_resource_id", "resource_id"),
        CheckConstraint("score >= 0 AND score <= 1", name="chk_recommendations_score"),
    )
