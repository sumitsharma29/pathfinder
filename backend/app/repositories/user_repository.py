import uuid
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.learner_profile import LearnerProfile


class UserRepository:
    """Repository handling database operations for Users and LearnerProfiles."""

    @staticmethod
    def get_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
        """Fetch user by ID."""
        return db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Fetch user by normalized email."""
        return db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    @staticmethod
    def create_user_with_profile(
        db: Session,
        name: str,
        email: str,
        password_hash: str,
        is_active: bool = True,
        target_role_id: Optional[uuid.UUID] = None,
        experience_level: Optional[str] = None
    ) -> Tuple[User, LearnerProfile]:
        """Atomically create User and associated LearnerProfile within the current transaction."""
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            is_active=is_active
        )
        db.add(user)
        db.flush()  # Flush to generate user.id

        profile = LearnerProfile(
            user_id=user.id,
            target_role_id=target_role_id,
            experience_level=experience_level,
            learning_preferences={}
        )
        db.add(profile)
        db.flush()

        return user, profile

    @staticmethod
    def update(db: Session, user: User) -> User:
        """Update user entity."""
        db.add(user)
        db.flush()
        return user
