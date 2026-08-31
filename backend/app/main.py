from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from backend.app.core.config import settings
from backend.app.core.exceptions import (
    AppException, app_exception_handler,
    validation_exception_handler, generic_exception_handler
)
from backend.app.api.router import api_router
from backend.app.db.session import engine

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    description="PathFinder AI — Intelligent Personalized Learning Navigation Platform REST API"
)

# ------------------------------------------------------------------------------
# 1. CORS MIDDLEWARE
# ------------------------------------------------------------------------------
if settings.CORS_ORIGINS:
    origins = [str(origin).strip() for origin in settings.CORS_ORIGINS if str(origin).strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=r"https://.*\.netlify\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


import uuid
from fastapi.responses import JSONResponse

# ------------------------------------------------------------------------------
# 2. SECURITY HEADERS & REQUEST CORRELATION MIDDLEWARE
# ------------------------------------------------------------------------------
@app.middleware("http")
async def security_and_tracing_middleware(request: Request, call_next):
    # Request Payload Size Limit Guard (SECURITY_SPEC.md §52)
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.MAX_REQUEST_BODY_BYTES:
        return JSONResponse(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            content={
                "success": False,
                "error": {
                    "code": "PAYLOAD_TOO_LARGE",
                    "message": f"Request body exceeds maximum allowed size of {settings.MAX_REQUEST_BODY_BYTES} bytes."
                }
            }
        )

    # Request ID Correlation (SECURITY_SPEC.md §43, DEPLOYMENT_SPEC.md §43)
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
    if settings.APP_ENV == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# ------------------------------------------------------------------------------
# 3. EXCEPTION HANDLERS
# ------------------------------------------------------------------------------
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# ------------------------------------------------------------------------------
# 4. HEALTH CHECK ENDPOINTS
# ------------------------------------------------------------------------------
@app.get("/health", tags=["Health"], summary="General health and version status")
def health_check():
    """Return safe application health, version, and environment status."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV
    }


@app.get("/health/live", tags=["Health"], summary="Liveness probe")
def liveness_check():
    """Process liveness probe."""
    return {"status": "ok"}


@app.get("/health/ready", tags=["Health"], summary="Readiness probe")
def readiness_check(response: Response):
    """Readiness probe checking database connectivity without touching external AI services."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected"
        }
    except Exception as e:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "unhealthy",
            "database": "unavailable"
        }


# ------------------------------------------------------------------------------
# 5. MOUNT ROUTERS
# ------------------------------------------------------------------------------
app.include_router(api_router, prefix="/api")
