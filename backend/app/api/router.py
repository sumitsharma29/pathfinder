from fastapi import APIRouter
from backend.app.api.v1.router import api_v1_router

api_router = APIRouter()

# Mount API v1 at /v1
api_router.include_router(api_v1_router, prefix="/v1")
