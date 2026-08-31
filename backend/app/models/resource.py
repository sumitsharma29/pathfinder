from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, Numeric, Boolean, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, Vector, JSONB
from backend.app.core.config import settings

if TYPE_CHECKING:
    from backend.app.models.resource_skill import ResourceSkill
    from backend.app.models.roadmap_item import RoadmapItem
    from backend.app.models.recommendation import Recommendation
    from backend.app.models.feedback import Feedback


class Resource(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "resources"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # course, tutorial, documentation, etc.
    provider: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    estimated_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False, index=True)
    meta_data: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, server_default="{}", nullable=False)
    embedding: Mapped[Optional[list]] = mapped_column(Vector(settings.EMBEDDING_DIMENSION), nullable=True)

    # Relationships
    resource_skills: Mapped[List["ResourceSkill"]] = relationship(
        "ResourceSkill",
        back_populates="resource",
        cascade="all, delete-orphan"
    )
    roadmap_items: Mapped[List["RoadmapItem"]] = relationship(
        "RoadmapItem",
        back_populates="resource"
    )
    recommendations: Mapped[List["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="resource"
    )
    feedbacks: Mapped[List["Feedback"]] = relationship(
        "Feedback",
        back_populates="resource"
    )

    __table_args__ = (
        Index("idx_resources_type", "resource_type"),
        Index("idx_resources_is_active", "is_active"),
        CheckConstraint("quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 100)", name="chk_resources_quality_score"),
        CheckConstraint("estimated_minutes IS NULL OR estimated_minutes > 0", name="chk_resources_estimated_minutes"),
    )
