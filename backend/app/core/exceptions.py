from typing import Optional, Any, Dict
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class AppException(Exception):
    """Base application exception."""
    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Any] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Raised when authentication fails or is missing."""
    def __init__(self, message: str = "Invalid credentials", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="UNAUTHENTICATED",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class AuthorizationError(AppException):
    """Raised when user lacks permission for a resource."""
    def __init__(self, message: str = "Access forbidden", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class NotFoundError(AppException):
    """Raised when requested resource does not exist."""
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class ConflictError(AppException):
    """Raised when an operation conflicts with existing state (e.g. duplicate email)."""
    def __init__(self, message: str = "Resource conflict", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class RateLimitExceededError(AppException):
    """Raised when client exceeds rate limit."""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after_seconds": retry_after}
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Central FastAPI handler for application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Central FastAPI handler for Pydantic validation errors."""
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        errors.append({
            "field": loc,
            "message": err.get("msg"),
            "type": err.get("type")
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY if hasattr(status, "HTTP_422_UNPROCESSABLE_ENTITY") else 422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed",
                "details": errors
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for unhandled internal exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected internal server error occurred",
                "details": None
            }
        }
    )
