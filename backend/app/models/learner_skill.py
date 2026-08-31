import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Numeric, DateTime, ForeignKey, Index, CheckConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.learner_profile import LearnerProfile
    from backend.app.models.skill import Skill


class LearnerSkill(Base):
    __tablename__ = "learner_skills"

    learner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learner_profiles.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    proficiency: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    source: Mapped[str] = mapped_column(String(30), nullable=False)  # self_declared, assessment, imported, inferred
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(5, 4), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )

    # Relationships
    learner: Mapped["LearnerProfile"] = relationship("LearnerProfile", back_populates="learner_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="learner_skills")

    __table_args__ = (
        Index("idx_learner_skills_learner_id", "learner_id"),
        Index("idx_learner_skills_skill_id", "skill_id"),
        CheckConstraint("proficiency >= 0 AND proficiency <= 100", name="chk_learner_skills_proficiency"),
        CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 1)", name="chk_learner_skills_confidence"),
    )
