from app.models.user import UserModel
from app.core.enums import UserRole
from app.core.exceptions import ForbiddenException


def require_admin(current_user: UserModel) -> UserModel:
    """Raise 403 if the current user is not an admin."""
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException("Admin access required.")
    return current_user


def require_associate_or_admin(current_user: UserModel) -> UserModel:
    """Raise 403 if the current user is a customer."""
    if current_user.role == UserRole.CUSTOMER:
        raise ForbiddenException("Associate or admin access required.")
    return current_user


def require_customer(current_user: UserModel) -> UserModel:
    """Raise 403 if the current user is not a customer."""
    if current_user.role != UserRole.CUSTOMER:
        raise ForbiddenException("Customer access required.")
    return current_user


def is_admin(user: UserModel) -> bool:
    return user.role == UserRole.ADMIN


def is_associate(user: UserModel) -> bool:
    return user.role == UserRole.ASSOCIATE


def is_customer(user: UserModel) -> bool:
    return user.role == UserRole.CUSTOMER


def can_access_resource(current_user: UserModel, owner_id: str) -> bool:
    """
    Returns True if the user can access a resource.
    Admins can access everything.
    Others can only access resources they own.
    """
    return is_admin(current_user) or current_user.id == owner_id
