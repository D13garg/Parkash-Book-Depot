from app.models.project import ProjectModel
from app.models.user import UserModel
from app.core.exceptions import ForbiddenException
from app.permissions.role_permissions import is_admin, is_associate


def assert_can_view_project(current_user: UserModel, project: ProjectModel) -> None:
    """
    Admin can view any project.
    Associate can only view projects assigned to them.
    Customers cannot view internal projects at all.
    """
    if is_admin(current_user):
        return
    if is_associate(current_user) and project.assigned_to == current_user.id:
        return
    raise ForbiddenException("You do not have access to this project.")


def assert_can_update_project(current_user: UserModel, project: ProjectModel) -> None:
    """
    Admin can update any project.
    Associate can only add updates to projects assigned to them.
    """
    if is_admin(current_user):
        return
    if is_associate(current_user) and project.assigned_to == current_user.id:
        return
    raise ForbiddenException("You can only update projects assigned to you.")
