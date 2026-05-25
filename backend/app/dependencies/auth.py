from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.database import get_db
from app.services.auth_service import AuthService
from app.permissions.role_permissions import require_admin, require_associate_or_admin
from app.models.user import UserModel

# Extracts the Bearer token from the Authorization header
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> UserModel:
    """
    Core auth dependency — validates JWT and returns the current user.
    Use this on any route that requires authentication.

    Usage:
        @router.get("/me")
        async def me(current_user: UserModel = Depends(get_current_user)):
            ...
    """
    service = AuthService(db)
    return await service.get_current_user_by_token(credentials.credentials)


async def get_current_admin(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    Dependency for admin-only routes.
    Raises 403 if user is not an admin.
    """
    return require_admin(current_user)


async def get_current_associate_or_admin(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    Dependency for routes accessible by associates and admins.
    Raises 403 if user is a customer.
    """
    return require_associate_or_admin(current_user)
