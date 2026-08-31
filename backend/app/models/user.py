from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.learner_profile import LearnerProfile


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)

    # Relationships
    profile: Mapped[Optional["LearnerProfile"]] = relationship(
        "LearnerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_users_email", "email"),
    )
