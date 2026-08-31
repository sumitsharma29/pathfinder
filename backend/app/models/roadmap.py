import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.learner_profile import LearnerProfile
    from backend.app.models.role import Role
    from backend.app.models.roadmap_item import RoadmapItem
    from backend.app.models.roadmap_version import RoadmapVersion


class Roadmap(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "roadmaps"

    learner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learner_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    target_role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active", server_default="'active'", nullable=False, index=True)
    estimated_weeks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    learner: Mapped["LearnerProfile"] = relationship("LearnerProfile", back_populates="roadmaps")
    target_role: Mapped["Role"] = relationship("Role", back_populates="roadmaps")
    items: Mapped[List["RoadmapItem"]] = relationship(
        "RoadmapItem",
        back_populates="roadmap",
        cascade="all, delete-orphan",
        order_by="RoadmapItem.sequence"
    )
    versions: Mapped[List["RoadmapVersion"]] = relationship(
        "RoadmapVersion",
        back_populates="roadmap",
        cascade="all, delete-orphan",
        order_by="RoadmapVersion.version"
    )

    __table_args__ = (
        UniqueConstraint("learner_id", "version", name="uq_roadmaps_learner_version"),
        Index("idx_roadmaps_learner_id", "learner_id"),
        Index("idx_roadmaps_target_role_id", "target_role_id"),
        Index("idx_roadmaps_status", "status"),
        CheckConstraint("version >= 1", name="chk_roadmaps_version"),
        CheckConstraint("estimated_weeks IS NULL OR estimated_weeks > 0", name="chk_roadmaps_estimated_weeks"),
    )
