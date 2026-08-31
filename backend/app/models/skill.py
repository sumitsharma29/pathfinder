from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, Numeric, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.role_skill import RoleSkill
    from backend.app.models.learner_skill import LearnerSkill
    from backend.app.models.skill_prerequisite import SkillPrerequisite
    from backend.app.models.resource_skill import ResourceSkill
    from backend.app.models.project_skill import ProjectSkill
    from backend.app.models.assessment import Assessment
    from backend.app.models.roadmap_item import RoadmapItem
    from backend.app.models.recommendation import Recommendation


class Skill(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    estimated_hours: Mapped[Optional[float]] = mapped_column(Numeric(8, 2), nullable=True)

    # Relationships
    role_skills: Mapped[List["RoleSkill"]] = relationship(
        "RoleSkill",
        back_populates="skill",
        cascade="all, delete-orphan"
    )
    learner_skills: Mapped[List["LearnerSkill"]] = relationship(
        "LearnerSkill",
        back_populates="skill",
        cascade="all, delete-orphan"
    )
    prerequisites: Mapped[List["SkillPrerequisite"]] = relationship(
        "SkillPrerequisite",
        foreign_keys="SkillPrerequisite.skill_id",
        back_populates="skill",
        cascade="all, delete-orphan"
    )
    dependent_skills: Mapped[List["SkillPrerequisite"]] = relationship(
        "SkillPrerequisite",
        foreign_keys="SkillPrerequisite.prerequisite_skill_id",
        back_populates="prerequisite_skill",
        cascade="all, delete-orphan"
    )
    resource_skills: Mapped[List["ResourceSkill"]] = relationship(
        "ResourceSkill",
        back_populates="skill",
        cascade="all, delete-orphan"
    )
    project_skills: Mapped[List["ProjectSkill"]] = relationship(
        "ProjectSkill",
        back_populates="skill",
        cascade="all, delete-orphan"
    )
    assessments: Mapped[List["Assessment"]] = relationship(
        "Assessment",
        back_populates="skill"
    )
    roadmap_items: Mapped[List["RoadmapItem"]] = relationship(
        "RoadmapItem",
        back_populates="skill"
    )
    recommendations: Mapped[List["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="skill"
    )

    __table_args__ = (
        Index("idx_skills_slug", "slug"),
        Index("idx_skills_category", "category"),
        CheckConstraint("estimated_hours >= 0", name="chk_skills_estimated_hours"),
    )
