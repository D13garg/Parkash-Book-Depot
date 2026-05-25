from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, books, project_requests, projects

# This is the single router mounted in main.py
# Every new feature router gets added here
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(auth.router,             prefix="/auth",             tags=["Auth"])
api_router.include_router(books.router,            prefix="/books",            tags=["Books"])
api_router.include_router(project_requests.router, prefix="/project-requests", tags=["Project Requests"])
api_router.include_router(projects.router,         prefix="/projects",         tags=["Projects"])

# All core backend phases complete.
# Remaining: orders, notifications, analytics (Phase 6+)