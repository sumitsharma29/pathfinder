from fastapi import APIRouter, Depends, Request, status, Response
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.auth import (
    RegisterRequest, LoginRequest, AuthResponse,
    AuthData, UserResponse, UserMeResponse
)
from backend.app.services.auth_service import AuthService
from backend.app.api.deps import get_current_active_user
from backend.app.models.user import User
from backend.app.core.security import auth_rate_limiter
from backend.app.core.exceptions import RateLimitExceededError

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new learner account"
)
def register(
    register_in: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Create a new user account with initial learner profile and return a JWT access token."""
    user, access_token = AuthService.register(db=db, register_in=register_in)
    return AuthResponse(
        success=True,
        data=AuthData(
            user=UserResponse(
                id=user.id,
                name=user.name,
                email=user.email
            ),
            access_token=access_token,
            token_type="bearer"
        ),
        message="Account created successfully"
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate existing user"
)
def login(
    request: Request,
    login_in: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate with email and password and return a JWT access token."""
    # Rate limit check by client IP / email
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"login:{client_ip}:{login_in.email.lower()}"
    allowed, retry_after = auth_rate_limiter.is_allowed(rate_key)
    if not allowed:
        raise RateLimitExceededError(
            message="Too many login attempts. Please try again later.",
            retry_after=retry_after
        )

    user, access_token = AuthService.authenticate(db=db, login_in=login_in)
    
    # Successful login: reset rate limiter for this user
    auth_rate_limiter.reset(rate_key)

    return AuthResponse(
        success=True,
        data=AuthData(
            user=UserResponse(
                id=user.id,
                name=user.name,
                email=user.email
            ),
            access_token=access_token,
            token_type="bearer"
        ),
        message="Login successful"
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout authenticated user"
)
def logout(
    current_user: User = Depends(get_current_active_user)
):
    """Stateless JWT logout acknowledgment. Client discards the token."""
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/me",
    response_model=UserMeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile"
)
def get_me(
    current_user: User = Depends(get_current_active_user)
):
    """Return identity and safe profile details of current authenticated user."""
    return UserMeResponse(
        success=True,
        data=UserResponse(
            id=current_user.id,
            name=current_user.name,
            email=current_user.email
        ),
        message="Authenticated user"
    )
