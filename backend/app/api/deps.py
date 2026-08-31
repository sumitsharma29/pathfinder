import uuid
from typing import Generator, Optional
from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.core.security import decode_access_token
from backend.app.core.exceptions import AuthenticationError, AuthorizationError
from backend.app.repositories.user_repository import UserRepository
from backend.app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False
)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Validate Bearer token and return authenticated User."""
    jwt_token = token
    if not jwt_token and authorization and authorization.startswith("Bearer "):
        jwt_token = authorization.split(" ")[1]

    if not jwt_token:
        raise AuthenticationError(message="Authentication token is required")

    payload = decode_access_token(jwt_token)
    if not payload or "sub" not in payload:
        raise AuthenticationError(message="Invalid or expired authentication token")

    try:
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, TypeError):
        raise AuthenticationError(message="Malformed token identity")

    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise AuthenticationError(message="User account no longer exists")

    if not user.is_active:
        raise AuthenticationError(message="User account is inactive")

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency verifying that authenticated user is active."""
    if not current_user.is_active:
        raise AuthenticationError(message="Inactive user account")
    return current_user


def verify_resource_ownership(owner_id: uuid.UUID, current_user: User) -> None:
    """Enforce data isolation: verify that the target owner matches current user."""
    if owner_id != current_user.id:
        raise AuthorizationError(message="You do not have permission to access this resource")
