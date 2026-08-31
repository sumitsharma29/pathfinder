import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Numeric, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.skill import Skill


class SkillPrerequisite(Base):
    __tablename__ = "skill_prerequisites"

    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    prerequisite_skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    strength: Mapped[float] = mapped_column(Numeric(5, 4), default=1.0, server_default="1.0", nullable=False)

    # Relationships
    skill: Mapped["Skill"] = relationship(
        "Skill",
        foreign_keys=[skill_id],
        back_populates="prerequisites"
    )
    prerequisite_skill: Mapped["Skill"] = relationship(
        "Skill",
        foreign_keys=[prerequisite_skill_id],
        back_populates="dependent_skills"
    )

    __table_args__ = (
        Index("idx_skill_prereq_skill_id", "skill_id"),
        Index("idx_skill_prereq_prereq_id", "prerequisite_skill_id"),
        CheckConstraint("skill_id != prerequisite_skill_id", name="chk_skill_prerequisites_no_self_ref"),
        CheckConstraint("strength >= 0 AND strength <= 1", name="chk_skill_prerequisites_strength"),
    )
