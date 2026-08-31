import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Numeric, Integer, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.user import User
    from backend.app.models.role import Role
    from backend.app.models.learner_skill import LearnerSkill
    from backend.app.models.roadmap import Roadmap
    from backend.app.models.assessment_result import AssessmentResult
    from backend.app.models.recommendation import Recommendation
    from backend.app.models.feedback import Feedback
    from backend.app.models.progress import Progress
    from backend.app.models.conversation import Conversation


class LearnerProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "learner_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    target_role_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )
    experience_level: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    daily_study_hours: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)
    target_duration_weeks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    learning_preferences: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}", nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")
    target_role: Mapped[Optional["Role"]] = relationship("Role", back_populates="learner_profiles")
    learner_skills: Mapped[List["LearnerSkill"]] = relationship(
        "LearnerSkill",
        back_populates="learner",
        cascade="all, delete-orphan"
    )
    roadmaps: Mapped[List["Roadmap"]] = relationship(
        "Roadmap",
        back_populates="learner",
        cascade="all, delete-orphan"
    )
    assessment_results: Mapped[List["AssessmentResult"]] = relationship(
        "AssessmentResult",
        back_populates="learner",
        cascade="all, delete-orphan"
    )
    recommendations: Mapped[List["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="learner",
        cascade="all, delete-orphan"
    )
    feedbacks: Mapped[List["Feedback"]] = relationship(
        "Feedback",
        back_populates="learner",
        cascade="all, delete-orphan"
    )
    progress_records: Mapped[List["Progress"]] = relationship(
        "Progress",
        back_populates="learner",
        cascade="all, delete-orphan"
    )
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation",
        back_populates="learner",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_learner_profiles_user_id", "user_id"),
        Index("idx_learner_profiles_target_role_id", "target_role_id"),
        CheckConstraint("daily_study_hours >= 0", name="chk_learner_daily_study_hours"),
        CheckConstraint("target_duration_weeks > 0", name="chk_learner_target_duration_weeks"),
    )
