from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, Numeric, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, Vector, JSONB
from backend.app.core.config import settings

if TYPE_CHECKING:
    from backend.app.models.project_skill import ProjectSkill
    from backend.app.models.roadmap_item import RoadmapItem


class Project(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "projects"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, index=True)
    estimated_hours: Mapped[Optional[float]] = mapped_column(Numeric(8, 2), nullable=True)
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_data: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, server_default="{}", nullable=False)
    embedding: Mapped[Optional[list]] = mapped_column(Vector(settings.EMBEDDING_DIMENSION), nullable=True)

    # Relationships
    project_skills: Mapped[List["ProjectSkill"]] = relationship(
        "ProjectSkill",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    roadmap_items: Mapped[List["RoadmapItem"]] = relationship(
        "RoadmapItem",
        back_populates="project"
    )

    __table_args__ = (
        Index("idx_projects_difficulty", "difficulty"),
        CheckConstraint("estimated_hours IS NULL OR estimated_hours > 0", name="chk_projects_estimated_hours"),
    )
