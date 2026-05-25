from fastapi import APIRouter, Depends, Query
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user, get_current_admin, get_current_associate_or_admin
from app.services.project_service import ProjectService
from app.schemas.project import (
    AssignProjectRequest,
    UpdateProjectStatusRequest,
    CreateProjectUpdateRequest,
    ProjectResponse,
    ProjectUpdateResponse,
)
from app.schemas.book import PaginatedResponse
from app.models.user import UserModel

router = APIRouter()


@router.post("/from-request/{request_id}", response_model=ProjectResponse, status_code=201)
async def convert_request_to_project(
    request_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin),
):
    """
    Convert an accepted customer request into an internal project.
    Admin only. Request must be in 'accepted' status.
    """
    service = ProjectService(db)
    return await service.convert_request_to_project(request_id, current_user)


@router.get("", response_model=PaginatedResponse[ProjectResponse])
async def list_projects(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = Query(default=None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_associate_or_admin),
):
    """
    List projects.
    - Admin: sees all projects, can filter by status.
    - Associate: sees only projects assigned to them.
    - Customer: blocked (403).
    """
    service = ProjectService(db)
    return await service.get_projects(current_user, page=page, page_size=page_size, status=status)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_associate_or_admin),
):
    """
    Get a single project.
    Admin can access any. Associate can only access their assigned project.
    """
    service = ProjectService(db)
    return await service.get_project(project_id, current_user)


@router.patch("/{project_id}/assign", response_model=ProjectResponse)
async def assign_associate(
    project_id: str,
    data: AssignProjectRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin),
):
    """
    Assign an associate to a project.
    Admin only. Moves project status from pending → assigned automatically.
    """
    service = ProjectService(db)
    return await service.assign_associate(project_id, data, current_user)


@router.patch("/{project_id}/status", response_model=ProjectResponse)
async def update_project_status(
    project_id: str,
    data: UpdateProjectStatusRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin),
):
    """
    Update project status. Admin only. State machine enforced.

    Valid transitions:
        pending → assigned / cancelled
        assigned → in_progress / cancelled
        in_progress → waiting_supplier / completed / cancelled
        waiting_supplier → in_progress / cancelled
    """
    service = ProjectService(db)
    return await service.update_status(project_id, data, current_user)


@router.post("/{project_id}/updates", response_model=ProjectUpdateResponse, status_code=201)
async def add_project_update(
    project_id: str,
    data: CreateProjectUpdateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_associate_or_admin),
):
    """
    Add a progress update / note to a project timeline.
    Admin can update any project.
    Associate can only update their assigned project.
    Optionally triggers a status change in the same call.
    """
    service = ProjectService(db)
    return await service.add_update(project_id, data, current_user)


@router.get("/{project_id}/updates", response_model=list[ProjectUpdateResponse])
async def get_project_updates(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_associate_or_admin),
):
    """
    Get the full timeline of updates for a project.
    Admin can view any. Associate can only view their assigned project's timeline.
    """
    service = ProjectService(db)
    return await service.get_updates(project_id, current_user)
