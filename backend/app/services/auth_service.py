from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.user_repository import UserRepository
from app.schemas.user import RegisterRequest, LoginRequest, TokenResponse, AccessTokenResponse, UserResponse
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import ConflictException, UnauthorizedException
from datetime import datetime, timezone
from app.core.enums import UserRole
from app.models.user import UserModel
from app.services.audit_log_service import audit
from app.services.error_log_service import log_error


def _to_user_response(user: UserModel) -> UserResponse:
    return UserResponse(
        id=user.id, name=user.name, email=user.email, role=user.role,
        is_active=user.is_active, phone=user.phone, address=user.address,
        created_at=user.created_at, updated_at=user.updated_at,
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
        self.db = db

    async def register(self, data: RegisterRequest) -> TokenResponse:
        if await self.user_repo.email_exists(data.email):
            raise ConflictException("A user with this email already exists.")
        now = datetime.now(timezone.utc)
        user_doc = {
            "name": data.name, "email": data.email,
            "hashed_password": hash_password(data.password),
            "role": UserRole.CUSTOMER.value, "is_active": True,
            "phone": data.phone, "address": data.address,
            "created_at": now, "updated_at": now,
        }
        user = await self.user_repo.create(user_doc)
        await audit(
            db=self.db, actor_id=user.id, actor_name=user.name,
            actor_role=user.role, action="user_registered",
            description=f"New customer account registered: {user.email}",
            entity_type="user", entity_id=user.id,
        )
        tokens = _make_tokens(user)
        return TokenResponse(**tokens, user=_to_user_response(user))

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.user_repo.find_by_email(data.email)
        if not user:
            await audit(
                db=self.db, actor_id="unknown", actor_name=data.email,
                actor_role="unknown", action="user_login_failed",
                description=f"Failed login attempt for email: {data.email}",
                metadata={"reason": "user_not_found"},
            )
            await log_error(
                db=self.db, message=f"Failed login - user not found: {data.email}",
                level="WARNING", endpoint="/auth/login", method="POST", status_code=401,
            )
            raise UnauthorizedException("Invalid email or password.")
        if not verify_password(data.password, user.hashed_password):
            await audit(
                db=self.db, actor_id=user.id, actor_name=user.name,
                actor_role=user.role, action="user_login_failed",
                description=f"Failed login attempt for: {user.email}",
                entity_type="user", entity_id=user.id,
                metadata={"reason": "wrong_password"},
            )
            raise UnauthorizedException("Invalid email or password.")
        if not user.is_active:
            raise UnauthorizedException("Your account has been deactivated.")
        tokens = _make_tokens(user)
        return TokenResponse(**tokens, user=_to_user_response(user))

    async def refresh(self, refresh_token: str) -> AccessTokenResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid or expired refresh token.")
        user = await self.user_repo.find_by_id(payload["sub"])
        if not user or not user.is_active:
            raise UnauthorizedException("User no longer exists.")
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