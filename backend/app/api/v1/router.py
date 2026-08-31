from fastapi import APIRouter
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.profile import router as profile_router
from backend.app.api.v1.skills import router as skills_router
from backend.app.api.v1.roles import router as roles_router
from backend.app.api.v1.skill_gaps import router as skill_gaps_router
from backend.app.api.v1.recommendations import router as recommendations_router
from backend.app.api.v1.roadmaps import router as roadmaps_router
from backend.app.api.v1.assessments import router as assessments_router
from backend.app.api.v1.progress import router as progress_router
from backend.app.api.v1.adaptive import router as adaptive_router
from backend.app.api.v1.goals import router as goals_router
from backend.app.api.v1.assistant import router as assistant_router
from backend.app.api.v1.resources import router as resources_router

api_v1_router = APIRouter()

# Include version 1 routers
api_v1_router.include_router(auth_router)
api_v1_router.include_router(profile_router)
api_v1_router.include_router(skills_router)
api_v1_router.include_router(roles_router)
api_v1_router.include_router(skill_gaps_router)
api_v1_router.include_router(recommendations_router)
api_v1_router.include_router(roadmaps_router)
api_v1_router.include_router(assessments_router)
api_v1_router.include_router(progress_router)
api_v1_router.include_router(adaptive_router)
api_v1_router.include_router(goals_router)
api_v1_router.include_router(assistant_router)
api_v1_router.include_router(resources_router)


