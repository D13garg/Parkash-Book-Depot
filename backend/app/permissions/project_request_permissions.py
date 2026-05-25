from app.models.project_request import ProjectRequestModel
from app.models.user import UserModel
from app.core.exceptions import ForbiddenException, BadRequestException
from app.permissions.role_permissions import is_admin


def assert_can_view_request(current_user: UserModel, request: ProjectRequestModel) -> None:
    """
    Admin can view any request.
    Customer can only view their own.
    """
    if not is_admin(current_user) and request.customer_id != current_user.id:
        raise ForbiddenException("You do not have access to this request.")


def assert_can_submit_request(current_user: UserModel) -> None:
    """Only customers can submit project requests."""
    from app.core.enums import UserRole
    if current_user.role != UserRole.CUSTOMER:
        raise ForbiddenException("Only customers can submit project requests.")


def assert_rejection_has_reason(status, rejection_reason: str) -> None:
    """If admin is rejecting a request, a reason must be provided."""
    from app.core.enums import ProjectRequestStatus
    if status == ProjectRequestStatus.REJECTED and not rejection_reason:
        raise BadRequestException("A rejection reason is required when rejecting a request.")
