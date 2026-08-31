import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Numeric, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.role import Role
    from backend.app.models.skill import Skill


class RoleSkill(Base):
    __tablename__ = "role_skills"

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    required_proficiency: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    importance: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    # Relationships
    role: Mapped["Role"] = relationship("Role", back_populates="role_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="role_skills")

    __table_args__ = (
        Index("idx_role_skills_role_id", "role_id"),
        Index("idx_role_skills_skill_id", "skill_id"),
        CheckConstraint("required_proficiency >= 0 AND required_proficiency <= 100", name="chk_role_skills_proficiency"),
        CheckConstraint("importance >= 0 AND importance <= 1", name="chk_role_skills_importance"),
    )
