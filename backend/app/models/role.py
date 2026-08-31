from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.role_skill import RoleSkill
    from backend.app.models.learner_profile import LearnerProfile
    from backend.app.models.roadmap import Roadmap


class Role(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    role_skills: Mapped[List["RoleSkill"]] = relationship(
        "RoleSkill",
        back_populates="role",
        cascade="all, delete-orphan"
    )
    learner_profiles: Mapped[List["LearnerProfile"]] = relationship(
        "LearnerProfile",
        back_populates="target_role"
    )
    roadmaps: Mapped[List["Roadmap"]] = relationship(
        "Roadmap",
        back_populates="target_role"
    )

    __table_args__ = (
        Index("idx_roles_slug", "slug"),
    )
