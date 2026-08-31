import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Numeric, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.resource import Resource
    from backend.app.models.skill import Skill


class ResourceSkill(Base):
    __tablename__ = "resource_skills"

    resource_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resources.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    coverage_weight: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)

    # Relationships
    resource: Mapped["Resource"] = relationship("Resource", back_populates="resource_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="resource_skills")

    __table_args__ = (
        Index("idx_resource_skills_resource_id", "resource_id"),
        Index("idx_resource_skills_skill_id", "skill_id"),
        CheckConstraint("coverage_weight >= 0 AND coverage_weight <= 1", name="chk_resource_skills_coverage_weight"),
    )
