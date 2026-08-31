import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey, Index, UniqueConstraint, CheckConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, JSONB

if TYPE_CHECKING:
    from backend.app.models.roadmap import Roadmap


class RoadmapVersion(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "roadmap_versions"

    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False)  # initial_generation, assessment, feedback, profile_change, adaptive_update, etc.
    reason: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )

    # Relationships
    roadmap: Mapped["Roadmap"] = relationship("Roadmap", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("roadmap_id", "version", name="uq_roadmap_versions_version"),
        Index("idx_roadmap_versions_roadmap_id", "roadmap_id"),
        CheckConstraint("version >= 1", name="chk_roadmap_versions_version"),
    )
