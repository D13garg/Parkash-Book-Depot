from fastapi import APIRouter
from app.api.v1.endpoints import (
    health, auth, books, project_requests,
    projects, reviews, notifications, gallery, users, audit_logs
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(auth.router,             prefix="/auth",             tags=["Auth"])
api_router.include_router(users.router,            prefix="/users",            tags=["Users"])
api_router.include_router(books.router,            prefix="/books",            tags=["Books"])
api_router.include_router(project_requests.router, prefix="/project-requests", tags=["Project Requests"])
api_router.include_router(projects.router,         prefix="/projects",         tags=["Projects"])
api_router.include_router(reviews.router,          prefix="/reviews",          tags=["Reviews"])
api_router.include_router(notifications.router,    prefix="/notifications",    tags=["Notifications"])
api_router.include_router(gallery.router,          prefix="/gallery",          tags=["Gallery"])
api_router.include_router(audit_logs.router,       prefix="/audit-logs",       tags=["Audit Logs"])