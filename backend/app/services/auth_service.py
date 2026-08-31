import uuid
from typing import Tuple
from sqlalchemy.orm import Session
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.core.exceptions import ConflictError, AuthenticationError
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.auth import RegisterRequest, LoginRequest
from backend.app.models.user import User


class AuthService:
    """Service handling business logic for authentication and user registration."""

    @staticmethod
    def normalize_email(email: str) -> str:
        """Trim surrounding whitespace and convert to lowercase."""
        if not email:
            return ""
        return email.strip().lower()

    @classmethod
    def register(cls, db: Session, register_in: RegisterRequest) -> Tuple[User, str]:
        """Register a new user, create their initial learner profile, and return (user, access_token)."""
        normalized_email = cls.normalize_email(register_in.email)
        
        # Check duplicate user
        existing_user = UserRepository.get_by_email(db, normalized_email)
        if existing_user:
            raise ConflictError(
                message="An account with this email address already exists",
                details={"field": "email"}
            )
        
        # Hash password securely
        hashed_pw = hash_password(register_in.password)

        # Create user and profile atomically
        user, _ = UserRepository.create_user_with_profile(
            db=db,
            name=register_in.name.strip(),
            email=normalized_email,
            password_hash=hashed_pw,
            is_active=True
        )
        db.commit()
        db.refresh(user)

        # Generate JWT access token
        access_token = create_access_token(subject=str(user.id))
        return user, access_token

    @classmethod
    def authenticate(cls, db: Session, login_in: LoginRequest) -> Tuple[User, str]:
        """Authenticate an existing user by email & password and return (user, access_token)."""
        normalized_email = cls.normalize_email(login_in.email)
        
        user = UserRepository.get_by_email(db, normalized_email)
        if not user:
            # Generic message to prevent user enumeration
            raise AuthenticationError(message="Invalid email or password")
        
        if not verify_password(login_in.password, user.password_hash):
            raise AuthenticationError(message="Invalid email or password")

        if not user.is_active:
            raise AuthenticationError(message="Account is inactive. Please contact support.")

        access_token = create_access_token(subject=str(user.id))
        return user, access_token
