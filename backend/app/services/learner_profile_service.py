import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.core.exceptions import NotFoundError, ConflictError
from backend.app.repositories.learner_profile_repository import LearnerProfileRepository
from backend.app.repositories.role_repository import RoleRepository
from backend.app.repositories.skill_repository import SkillRepository
from backend.app.schemas.profile import (
    LearnerProfileUpdateRequest, LearnerSkillCreateRequest,
    LearnerSkillUpdateRequest, LearnerSkillItemResponse
)
from backend.app.models.learner_profile import LearnerProfile


class LearnerProfileService:
    """Service managing learner profile lifecycle and learner skill portfolio."""

    @staticmethod
    def get_profile(db: Session, user_id: uuid.UUID) -> LearnerProfile:
        """Retrieve learner profile for the authenticated user."""
        profile = LearnerProfileRepository.get_by_user_id(db, user_id)
        if not profile:
            raise NotFoundError(message="Learner profile not found")
        return profile

    @classmethod
    def update_profile(
        cls,
        db: Session,
        user_id: uuid.UUID,
        update_in: LearnerProfileUpdateRequest
    ) -> LearnerProfile:
        """Update learner profile settings and target role."""
        profile = cls.get_profile(db, user_id)

        # Validate target role if provided
        if update_in.target_role_id:
            role = RoleRepository.get_by_id(db, update_in.target_role_id)
            if not role:
                raise NotFoundError(
                    message="Target role does not exist",
                    details={"target_role_id": str(update_in.target_role_id)}
                )

        updated = LearnerProfileRepository.update_profile(
            db=db,
            profile=profile,
            target_role_id=update_in.target_role_id,
            experience_level=update_in.experience_level,
            daily_study_hours=update_in.daily_study_hours,
            target_duration_weeks=update_in.target_duration_weeks,
            learning_preferences=update_in.learning_preferences
        )
        db.commit()
        db.refresh(updated)
        return updated

    @classmethod
    def get_learner_skills(cls, db: Session, user_id: uuid.UUID) -> List[LearnerSkillItemResponse]:
        """Retrieve all skills of the authenticated learner."""
        profile = cls.get_profile(db, user_id)
        skills = LearnerProfileRepository.get_learner_skills(db, profile.id)
        
        result = []
        for s in skills:
            result.append(
                LearnerSkillItemResponse(
                    skill_id=s.skill_id,
                    skill_name=s.skill.name if s.skill else "Unknown Skill",
                    skill_slug=s.skill.slug if s.skill else "",
                    category=s.skill.category if s.skill else None,
                    proficiency=float(s.proficiency),
                    source=s.source,
                    confidence=float(s.confidence) if s.confidence is not None else None
                )
            )
        return result

    @classmethod
    def add_learner_skill(
        cls,
        db: Session,
        user_id: uuid.UUID,
        skill_in: LearnerSkillCreateRequest
    ) -> LearnerSkillItemResponse:
        """Add a new skill to learner's portfolio."""
        profile = cls.get_profile(db, user_id)

        # Verify skill exists in catalog
        skill = SkillRepository.get_by_id(db, skill_in.skill_id)
        if not skill:
            raise NotFoundError(
                message="Skill not found in catalog",
                details={"skill_id": str(skill_in.skill_id)}
            )

        # Check if already declared
        existing = LearnerProfileRepository.get_learner_skill(db, profile.id, skill_in.skill_id)
        if existing:
            raise ConflictError(
                message="Skill already exists in your profile. Use update endpoint to change proficiency.",
                details={"skill_id": str(skill_in.skill_id)}
            )

        ls = LearnerProfileRepository.add_or_update_learner_skill(
            db=db,
            learner_id=profile.id,
            skill_id=skill_in.skill_id,
            proficiency=skill_in.proficiency,
            source=skill_in.source,
            confidence=skill_in.confidence
        )
        db.commit()

        return LearnerSkillItemResponse(
            skill_id=skill.id,
            skill_name=skill.name,
            skill_slug=skill.slug,
            category=skill.category,
            proficiency=float(ls.proficiency),
            source=ls.source,
            confidence=float(ls.confidence) if ls.confidence is not None else None
        )

    @classmethod
    def update_learner_skill(
        cls,
        db: Session,
        user_id: uuid.UUID,
        skill_id: uuid.UUID,
        update_in: LearnerSkillUpdateRequest
    ) -> LearnerSkillItemResponse:
        """Update existing learner skill proficiency."""
        profile = cls.get_profile(db, user_id)

        existing = LearnerProfileRepository.get_learner_skill(db, profile.id, skill_id)
        if not existing:
            raise NotFoundError(
                message="Skill not found in your profile",
                details={"skill_id": str(skill_id)}
            )

        source = update_in.source or existing.source
        confidence = update_in.confidence if update_in.confidence is not None else existing.confidence

        ls = LearnerProfileRepository.add_or_update_learner_skill(
            db=db,
            learner_id=profile.id,
            skill_id=skill_id,
            proficiency=update_in.proficiency,
            source=source,
            confidence=confidence
        )
        db.commit()

        return LearnerSkillItemResponse(
            skill_id=existing.skill_id,
            skill_name=existing.skill.name if existing.skill else "Unknown Skill",
            skill_slug=existing.skill.slug if existing.skill else "",
            category=existing.skill.category if existing.skill else None,
            proficiency=float(ls.proficiency),
            source=ls.source,
            confidence=float(ls.confidence) if ls.confidence is not None else None
        )

    @classmethod
    def delete_learner_skill(cls, db: Session, user_id: uuid.UUID, skill_id: uuid.UUID) -> None:
        """Remove a skill from learner's profile."""
        profile = cls.get_profile(db, user_id)
        deleted = LearnerProfileRepository.delete_learner_skill(db, profile.id, skill_id)
        if not deleted:
            raise NotFoundError(
                message="Skill not found in your profile",
                details={"skill_id": str(skill_id)}
            )
        db.commit()
