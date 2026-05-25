from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.user_repository import UserRepository
from app.schemas.user import RegisterRequest, LoginRequest, TokenResponse, AccessTokenResponse, UserResponse
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import ConflictException, UnauthorizedException
from datetime import datetime, timezone
from app.core.enums import UserRole
from app.models.user import UserModel


def _to_user_response(user: UserModel) -> UserResponse:
    """Convert a UserModel (DB) into a UserResponse (API-safe)."""
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        phone=user.phone,
        address=user.address,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def _make_tokens(user: UserModel) -> dict:
    payload = {"sub": user.id, "role": user.role}
    return {
        "access_token": create_access_token(payload),
        "refresh_token": create_refresh_token(payload),
    }


class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.user_repo = UserRepository(db)

    async def register(self, data: RegisterRequest) -> TokenResponse:
        # 1. Check email is not already taken
        if await self.user_repo.email_exists(data.email):
            raise ConflictException("A user with this email already exists.")

        # 2. Hash password and build the document to store
        now = datetime.now(timezone.utc)
        user_doc = {
            "name": data.name,
            "email": data.email,
            "hashed_password": hash_password(data.password),
            "role": UserRole.CUSTOMER.value,  # all self-registrations are customers
            "is_active": True,
            "phone": data.phone,
            "address": data.address,
            "created_at": now,
            "updated_at": now,
        }

        # 3. Persist to MongoDB via repository
        user = await self.user_repo.create(user_doc)

        # 4. Issue tokens and return
        tokens = _make_tokens(user)
        return TokenResponse(**tokens, user=_to_user_response(user))

    async def login(self, data: LoginRequest) -> TokenResponse:
        # 1. Look up user by email
        user = await self.user_repo.find_by_email(data.email)
        if not user:
            raise UnauthorizedException("Invalid email or password.")

        # 2. Verify password
        if not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password.")

        # 3. Check account is active
        if not user.is_active:
            raise UnauthorizedException("Your account has been deactivated.")

        # 4. Issue tokens and return
        tokens = _make_tokens(user)
        return TokenResponse(**tokens, user=_to_user_response(user))

    async def refresh(self, refresh_token: str) -> AccessTokenResponse:
        # 1. Decode and validate the refresh token
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid or expired refresh token.")

        # 2. Confirm user still exists and is active
        user = await self.user_repo.find_by_id(payload["sub"])
        if not user or not user.is_active:
            raise UnauthorizedException("User no longer exists.")

        # 3. Issue a new access token only
        new_access_token = create_access_token({"sub": user.id, "role": user.role})
        return AccessTokenResponse(access_token=new_access_token)

    async def get_current_user_by_token(self, token: str) -> UserModel:
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise UnauthorizedException("Invalid or expired access token.")

        user = await self.user_repo.find_by_id(payload["sub"])
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or deactivated.")

        return user
