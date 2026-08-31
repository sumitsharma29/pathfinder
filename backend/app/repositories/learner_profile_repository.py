import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from backend.app.models.learner_profile import LearnerProfile
from backend.app.models.learner_skill import LearnerSkill
from backend.app.models.skill import Skill


class LearnerProfileRepository:
    """Repository handling database operations for Learner Profiles and Learner Skills."""

    @staticmethod
    def get_by_user_id(db: Session, user_id: uuid.UUID) -> Optional[LearnerProfile]:
        """Fetch profile by user ID, eagerly loading target role."""
        return db.execute(
            select(LearnerProfile)
            .options(joinedload(LearnerProfile.target_role))
            .where(LearnerProfile.user_id == user_id)
        ).scalar_one_or_none()

    @staticmethod
    def get_by_id(db: Session, profile_id: uuid.UUID) -> Optional[LearnerProfile]:
        """Fetch profile by ID."""
        return db.execute(
            select(LearnerProfile)
            .options(joinedload(LearnerProfile.target_role))
            .where(LearnerProfile.id == profile_id)
        ).scalar_one_or_none()

    @staticmethod
    def update_profile(
        db: Session,
        profile: LearnerProfile,
        target_role_id: Optional[uuid.UUID] = None,
        experience_level: Optional[str] = None,
        daily_study_hours: Optional[float] = None,
        target_duration_weeks: Optional[int] = None,
        learning_preferences: Optional[dict] = None
    ) -> LearnerProfile:
        """Update learner profile fields."""
        if target_role_id is not None:
            profile.target_role_id = target_role_id
        if experience_level is not None:
            profile.experience_level = experience_level
        if daily_study_hours is not None:
            profile.daily_study_hours = daily_study_hours
        if target_duration_weeks is not None:
            profile.target_duration_weeks = target_duration_weeks
        if learning_preferences is not None:
            profile.learning_preferences = learning_preferences

        db.add(profile)
        db.flush()
        return profile

    @staticmethod
    def get_learner_skills(db: Session, learner_id: uuid.UUID) -> List[LearnerSkill]:
        """Retrieve all skills declared/acquired by the learner with skill details."""
        return db.execute(
            select(LearnerSkill)
            .options(joinedload(LearnerSkill.skill))
            .where(LearnerSkill.learner_id == learner_id)
        ).scalars().all()

    @staticmethod
    def get_learner_skill(db: Session, learner_id: uuid.UUID, skill_id: uuid.UUID) -> Optional[LearnerSkill]:
        """Retrieve a specific learner skill entry."""
        return db.execute(
            select(LearnerSkill)
            .options(joinedload(LearnerSkill.skill))
            .where(
                LearnerSkill.learner_id == learner_id,
                LearnerSkill.skill_id == skill_id
            )
        ).scalar_one_or_none()

    @staticmethod
    def add_or_update_learner_skill(
        db: Session,
        learner_id: uuid.UUID,
        skill_id: uuid.UUID,
        proficiency: float,
        source: str = "self_declared",
        confidence: Optional[float] = 1.0
    ) -> LearnerSkill:
        """Add new learner skill or update existing proficiency."""
        ls = db.execute(
            select(LearnerSkill).where(
                LearnerSkill.learner_id == learner_id,
                LearnerSkill.skill_id == skill_id
            )
        ).scalar_one_or_none()

        if ls:
            ls.proficiency = proficiency
            if source:
                ls.source = source
            if confidence is not None:
                ls.confidence = confidence
        else:
            ls = LearnerSkill(
                learner_id=learner_id,
                skill_id=skill_id,
                proficiency=proficiency,
                source=source,
                confidence=confidence
            )
            db.add(ls)

        db.flush()
        return ls

    @staticmethod
    def delete_learner_skill(db: Session, learner_id: uuid.UUID, skill_id: uuid.UUID) -> bool:
        """Remove a learner skill entry."""
        ls = db.execute(
            select(LearnerSkill).where(
                LearnerSkill.learner_id == learner_id,
                LearnerSkill.skill_id == skill_id
            )
        ).scalar_one_or_none()

        if not ls:
            return False

        db.delete(ls)
        db.flush()
        return True
