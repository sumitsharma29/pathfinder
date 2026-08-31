import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, Numeric, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.skill import Skill
    from backend.app.models.assessment_question import AssessmentQuestion
    from backend.app.models.assessment_result import AssessmentResult
    from backend.app.models.roadmap_item import RoadmapItem


class Assessment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "assessments"

    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    passing_score: Mapped[float] = mapped_column(Numeric(5, 2), default=70.0, server_default="70.0", nullable=False)

    # Relationships
    skill: Mapped["Skill"] = relationship("Skill", back_populates="assessments")
    questions: Mapped[List["AssessmentQuestion"]] = relationship(
        "AssessmentQuestion",
        back_populates="assessment",
        cascade="all, delete-orphan"
    )
    results: Mapped[List["AssessmentResult"]] = relationship(
        "AssessmentResult",
        back_populates="assessment"
    )
    roadmap_items: Mapped[List["RoadmapItem"]] = relationship(
        "RoadmapItem",
        back_populates="assessment"
    )

    __table_args__ = (
        Index("idx_assessments_skill_id", "skill_id"),
        CheckConstraint("passing_score >= 0 AND passing_score <= 100", name="chk_assessments_passing_score"),
    )
