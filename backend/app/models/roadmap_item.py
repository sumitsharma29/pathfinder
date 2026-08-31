
import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, Numeric, ForeignKey, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.roadmap import Roadmap
    from backend.app.models.skill import Skill
    from backend.app.models.resource import Resource
    from backend.app.models.project import Project
    from backend.app.models.assessment import Assessment
    from backend.app.models.progress import Progress


class RoadmapItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "roadmap_items"

    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
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
        nullable=True
    )
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="RESTRICT"),
        nullable=True
    )
    assessment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="RESTRICT"),
        nullable=True
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="LOCKED", server_default="'LOCKED'", nullable=False, index=True)
    progress: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, server_default="0.0", nullable=False)
    estimated_hours: Mapped[Optional[float]] = mapped_column(Numeric(8, 2), nullable=True)
    reason: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    locked_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    roadmap: Mapped["Roadmap"] = relationship("Roadmap", back_populates="items")
    skill: Mapped[Optional["Skill"]] = relationship("Skill", back_populates="roadmap_items")
    resource: Mapped[Optional["Resource"]] = relationship("Resource", back_populates="roadmap_items")
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="roadmap_items")
    assessment: Mapped[Optional["Assessment"]] = relationship("Assessment", back_populates="roadmap_items")
    progress_records: Mapped[List["Progress"]] = relationship(
        "Progress",
        back_populates="roadmap_item",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("roadmap_id", "sequence", name="uq_roadmap_items_sequence"),
        Index("idx_roadmap_items_roadmap_id", "roadmap_id"),
        Index("idx_roadmap_items_sequence", "sequence"),
        Index("idx_roadmap_items_status", "status"),
        CheckConstraint("sequence >= 1", name="chk_roadmap_items_sequence"),
        CheckConstraint("progress >= 0 AND progress <= 100", name="chk_roadmap_items_progress"),
    )
