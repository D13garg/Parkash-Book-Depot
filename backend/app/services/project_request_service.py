import math
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.repositories.project_request_repository import ProjectRequestRepository
from app.schemas.project_request import (
    CreateProjectRequestRequest,
    UpdateRequestStatusRequest,
    ProjectRequestResponse,
)
from app.schemas.book import PaginatedResponse
from app.models.project_request import ProjectRequestModel
from app.models.user import UserModel
from app.core.enums import is_valid_request_transition
from app.core.exceptions import NotFoundException, InvalidStateTransitionException
from app.permissions.project_request_permissions import (
    assert_can_view_request,
    assert_can_submit_request,
    assert_rejection_has_reason,
)
from app.permissions.role_permissions import is_admin


def _to_response(req: ProjectRequestModel) -> ProjectRequestResponse:
    return ProjectRequestResponse(
        id=req.id,
        customer_id=req.customer_id,
        title=req.title,
        description=req.description,
        category=req.category,
        requirements=req.requirements,
        quantity=req.quantity,
        institution_name=req.institution_name,
        institution_address=req.institution_address,
        contact_phone=req.contact_phone,
        status=req.status,
        admin_notes=req.admin_notes,
        rejection_reason=req.rejection_reason,
        created_at=req.created_at,
        updated_at=req.updated_at,
    )


class ProjectRequestService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = ProjectRequestRepository(db)

    async def submit_request(
        self,
        data: CreateProjectRequestRequest,
        current_user: UserModel,
    ) -> ProjectRequestResponse:
        # Only customers can submit
        assert_can_submit_request(current_user)

        doc = data.model_dump()
        doc["customer_id"] = current_user.id
        doc["status"] = "submitted"

        request = await self.repo.create(doc)
        return _to_response(request)

    async def get_requests(
        self,
        current_user: UserModel,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
    ) -> PaginatedResponse[ProjectRequestResponse]:
        skip = (page - 1) * page_size

        # Admins see all requests; customers see only their own
        if is_admin(current_user):
            requests, total = await self.repo.find_all(status=status, skip=skip, limit=page_size)
        else:
            requests, total = await self.repo.find_by_customer(current_user.id, skip=skip, limit=page_size)

        return PaginatedResponse(
            items=[_to_response(r) for r in requests],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 1,
        )

    async def get_request(
        self,
        request_id: str,
        current_user: UserModel,
    ) -> ProjectRequestResponse:
        request = await self.repo.find_by_id(request_id)
        if not request:
            raise NotFoundException("Project request")

        # Ownership check — customers can only see their own
        assert_can_view_request(current_user, request)
        return _to_response(request)

    async def update_status(
        self,
        request_id: str,
        data: UpdateRequestStatusRequest,
        current_user: UserModel,
    ) -> ProjectRequestResponse:
        request = await self.repo.find_by_id(request_id)
        if not request:
            raise NotFoundException("Project request")

        # State machine — reject invalid transitions
        if not is_valid_request_transition(request.status, data.status):
            raise InvalidStateTransitionException(
                current=request.status.value,
                attempted=data.status.value,
            )

        # Rejection must include a reason
        assert_rejection_has_reason(data.status, data.rejection_reason)

        update_data = {"status": data.status.value}
        if data.admin_notes:
            update_data["admin_notes"] = data.admin_notes
        if data.rejection_reason:
            update_data["rejection_reason"] = data.rejection_reason

        updated = await self.repo.update_status(request_id, update_data)
        return _to_response(updated)
