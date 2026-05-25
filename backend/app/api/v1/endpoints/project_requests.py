from fastapi import APIRouter, Depends, Query
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user, get_current_admin
from app.services.project_request_service import ProjectRequestService
from app.schemas.project_request import (
    CreateProjectRequestRequest,
    UpdateRequestStatusRequest,
    ProjectRequestResponse,
)
from app.schemas.book import PaginatedResponse
from app.models.user import UserModel

router = APIRouter()


@router.post("", response_model=ProjectRequestResponse, status_code=201)
async def submit_request(
    data: CreateProjectRequestRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Submit a new project request.
    Only customers can submit. Associates and admins are blocked at the permission layer.
    """
    service = ProjectRequestService(db)
    return await service.submit_request(data, current_user)


@router.get("", response_model=PaginatedResponse[ProjectRequestResponse])
async def list_requests(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = Query(default=None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    List project requests.
    - Admin: sees all requests, can filter by status.
    - Customer: sees only their own requests.
    """
    service = ProjectRequestService(db)
    return await service.get_requests(current_user, page=page, page_size=page_size, status=status)


@router.get("/{request_id}", response_model=ProjectRequestResponse)
async def get_request(
    request_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get a single project request by ID.
    Admin can access any. Customer can only access their own.
    """
    service = ProjectRequestService(db)
    return await service.get_request(request_id, current_user)


@router.patch("/{request_id}/status", response_model=ProjectRequestResponse)
async def update_status(
    request_id: str,
    data: UpdateRequestStatusRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: UserModel = Depends(get_current_admin),       # admin only
    current_user: UserModel = Depends(get_current_user),
):
    """
    Update the status of a project request.
    Admin only. State machine enforced — invalid transitions are rejected.

    Valid flow:
        submitted → under_review → accepted / rejected
        accepted → converted_to_project  (happens automatically in Phase 5)
    """
    service = ProjectRequestService(db)
    return await service.update_status(request_id, data, current_user)
