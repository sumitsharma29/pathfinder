import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Numeric, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, JSONB

if TYPE_CHECKING:
    from backend.app.models.assessment import Assessment


class AssessmentQuestion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "assessment_questions"

    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(40), nullable=False)  # multiple_choice, single_choice, true_false
    options: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    points: Mapped[float] = mapped_column(Numeric(8, 2), default=1.0, server_default="1.0", nullable=False)

    # Relationships
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="questions")

    __table_args__ = (
        Index("idx_assessment_questions_assessment_id", "assessment_id"),
        CheckConstraint("points > 0", name="chk_assessment_questions_points"),
    )
