import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import Numeric, Integer, DateTime, ForeignKey, Index, UniqueConstraint, CheckConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.models.assessment import Assessment
    from backend.app.models.learner_profile import LearnerProfile


class AssessmentResult(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "assessment_results"

    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    learner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learner_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    skill_mastery: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )

    # Relationships
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="results")
    learner: Mapped["LearnerProfile"] = relationship("LearnerProfile", back_populates="assessment_results")

    __table_args__ = (
        UniqueConstraint("assessment_id", "learner_id", "attempt_number", name="uq_assessment_results_attempt"),
        Index("idx_assessment_results_learner_id", "learner_id"),
        Index("idx_assessment_results_assessment_id", "assessment_id"),
        CheckConstraint("score >= 0 AND score <= 100", name="chk_assessment_results_score"),
        CheckConstraint("skill_mastery >= 0 AND skill_mastery <= 100", name="chk_assessment_results_mastery"),
        CheckConstraint("attempt_number >= 1", name="chk_assessment_results_attempt_number"),
    )
