import time
import logging
import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone

from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    LoginRequest, TokenResponse, AccessTokenResponse, UserResponse,
    RegisterInitiateRequest, OTPVerifyRequest, OTPInitiateResponse,
    ForgotPasswordVerifyRequest, GoogleAuthRequest,
)
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
)
from app.core.exceptions import (
    ConflictException, UnauthorizedException, BadRequestException,
)
from app.core.enums import UserRole
from app.core.config import settings
from app.models.user import UserModel
from app.services.audit_log_service import audit
from app.services.error_log_service import log_error
from app.services.metrics_service import increment as inc_metric
from app.services.otp_service import OTPService
from app.services.email_service import send_otp_email

logger = logging.getLogger(__name__)

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


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
        self.otp_service = OTPService(db)
        self.db = db

    # ── Step 1: Initiate registration — validate, store pending, send OTP ────

    async def register_initiate(self, data: RegisterInitiateRequest) -> OTPInitiateResponse:
        if await self.user_repo.email_exists(data.email):
            raise ConflictException("A user with this email already exists.")

        # Hash the password NOW so it's never stored plain in pending_data
        pending_data = {
            "name": data.name,
            "email": data.email,
            "hashed_password": hash_password(data.password),
            "phone": data.phone,
            "address": data.address,
        }

        code = await self.otp_service.create_otp(
            email=data.email,
            purpose="register",
            pending_data=pending_data,
        )

        await send_otp_email(data.email, code, purpose="register")

        return OTPInitiateResponse(
            message="Verification code sent to your email. It expires in 3 minutes.",
            email=data.email,
        )

    # ── Step 2: Verify OTP → create user → return tokens ─────────────────────

    async def register_verify(self, data: OTPVerifyRequest) -> TokenResponse:
        pending_data = await self.otp_service.verify_otp(
            email=data.email,
            code=data.code,
            purpose="register",
        )

        if not pending_data:
            raise BadRequestException("Registration data not found. Please start over.")

        # Double-check email isn't taken in the window between initiate and verify
        if await self.user_repo.email_exists(data.email):
            raise ConflictException("A user with this email already exists.")

        now = datetime.now(timezone.utc)
        user_doc = {
            "name": pending_data["name"],
            "email": pending_data["email"],
            "hashed_password": pending_data["hashed_password"],   # already bcrypt+peppered
            "role": UserRole.CUSTOMER.value,
            "is_active": True,
            "phone": pending_data.get("phone"),
            "address": pending_data.get("address"),
            "created_at": now,
            "updated_at": now,
        }
        user = await self.user_repo.create(user_doc)

        await audit(
            db=self.db, actor_id=user.id, actor_name=user.name,
            actor_role=user.role, action="user_registered",
            description=f"New customer account registered (email verified): {user.email}",
            entity_type="user", entity_id=user.id,
        )
        await inc_metric(self.db, "new_users")

        tokens = _make_tokens(user)
        return TokenResponse(**tokens, user=_to_user_response(user))

    # ── Login ─────────────────────────────────────────────────────────────────

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
            await inc_metric(self.db, "logins_failed")
            raise UnauthorizedException("Invalid email or password.")

        # Google-only accounts have no password
        if not user.hashed_password:
            raise UnauthorizedException(
                "This account uses Google Sign-In. Please sign in with Google."
            )

        if not verify_password(data.password, user.hashed_password):
            await audit(
                db=self.db, actor_id=user.id, actor_name=user.name,
                actor_role=user.role, action="user_login_failed",
                description=f"Failed login attempt for: {user.email}",
                entity_type="user", entity_id=user.id,
                metadata={"reason": "wrong_password"},
            )
            await inc_metric(self.db, "logins_failed")
            raise UnauthorizedException("Invalid email or password.")

        if not user.is_active:
            raise UnauthorizedException("Your account has been deactivated.")

        await inc_metric(self.db, "logins_success")
        tokens = _make_tokens(user)
        return TokenResponse(**tokens, user=_to_user_response(user))

    # ── Forgot password step 1: send OTP ─────────────────────────────────────

    async def forgot_password_initiate(self, email: str) -> None:
        """
        Always returns without error — prevents email enumeration.
        Only sends OTP if the email exists and belongs to a password-based account.
        """
        user = await self.user_repo.find_by_email(email)

        # If user not found or is a Google account — silently do nothing
        if not user or not user.hashed_password:
            logger.info(f"Forgot password requested for non-existent/Google email: {email}")
            return

        code = await self.otp_service.create_otp(
            email=email,
            purpose="forgot_password",
            pending_data=None,
        )
        await send_otp_email(email, code, purpose="forgot_password")

    # ── Forgot password step 2: verify OTP → reset password ──────────────────

    async def forgot_password_verify(self, data: ForgotPasswordVerifyRequest) -> None:
        # Verify OTP — raises on failure
        await self.otp_service.verify_otp(
            email=data.email,
            code=data.code,
            purpose="forgot_password",
        )

        user = await self.user_repo.find_by_email(data.email)
        if not user:
            raise UnauthorizedException("Invalid or expired verification code.")

        new_hash = hash_password(data.new_password)
        await self.user_repo.update(user.id, {
            "hashed_password": new_hash,
            "updated_at": datetime.now(timezone.utc),
        })

        await audit(
            db=self.db, actor_id=user.id, actor_name=user.name,
            actor_role=user.role, action="password_reset",
            description=f"Password reset via OTP for: {user.email}",
            entity_type="user", entity_id=user.id,
        )

    # ── Google OAuth ──────────────────────────────────────────────────────────

    async def google_auth(self, data: GoogleAuthRequest) -> TokenResponse:
        """
        Verify Google ID token with Google's tokeninfo endpoint.
        Creates account on first login, finds existing account on subsequent logins.
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                GOOGLE_TOKENINFO_URL,
                params={"id_token": data.id_token},
            )

        if resp.status_code != 200:
            raise UnauthorizedException("Invalid Google token. Please try again.")

        google_data = resp.json()

        # Validate audience — must be our client ID
        if google_data.get("aud") != settings.GOOGLE_CLIENT_ID:
            raise UnauthorizedException("Google token audience mismatch.")

        # Validate email is verified by Google
        if google_data.get("email_verified") != "true":
            raise UnauthorizedException("Google account email is not verified.")

        email = google_data.get("email")
        name = google_data.get("name") or email.split("@")[0]

        if not email:
            raise UnauthorizedException("Could not retrieve email from Google account.")

        # Find or create user
        user = await self.user_repo.find_by_email(email)
        if not user:
            now = datetime.now(timezone.utc)
            user_doc = {
                "name": name,
                "email": email,
                "hashed_password": None,    # Google accounts have no password
                "role": UserRole.CUSTOMER.value,
                "is_active": True,
                "phone": None,
                "address": None,
                "created_at": now,
                "updated_at": now,
            }
            user = await self.user_repo.create(user_doc)
            await audit(
                db=self.db, actor_id=user.id, actor_name=user.name,
                actor_role=user.role, action="user_registered",
                description=f"New customer registered via Google OAuth: {user.email}",
                entity_type="user", entity_id=user.id,
            )
            await inc_metric(self.db, "new_users")
        else:
            if not user.is_active:
                raise UnauthorizedException("Your account has been deactivated.")

        await inc_metric(self.db, "logins_success")
        tokens = _make_tokens(user)
        return TokenResponse(**tokens, user=_to_user_response(user))

    # ── Refresh token ─────────────────────────────────────────────────────────

    async def refresh(self, refresh_token: str) -> AccessTokenResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid or expired refresh token.")
        user = await self.user_repo.find_by_id(payload["sub"])
        if not user or not user.is_active:
            raise UnauthorizedException("User no longer exists.")
        new_access_token = create_access_token({"sub": user.id, "role": user.role})
        return AccessTokenResponse(access_token=new_access_token)

    # ── Get current user from token ───────────────────────────────────────────

    async def get_current_user_by_token(self, token: str) -> UserModel:
        perf_total_start = time.perf_counter()

        perf_jwt_start = time.perf_counter()
        payload = decode_token(token)
        perf_jwt_elapsed = time.perf_counter() - perf_jwt_start
        logger.debug(f"[PERF] JWT DECODE: {perf_jwt_elapsed:.3f}s")

        if not payload or payload.get("type") != "access":
            raise UnauthorizedException("Invalid or expired access token.")

        perf_lookup_start = time.perf_counter()
        user = await self.user_repo.find_by_id(payload["sub"])
        perf_lookup_elapsed = time.perf_counter() - perf_lookup_start
        logger.debug(f"[PERF] USER LOOKUP: {perf_lookup_elapsed:.3f}s (user_id={payload['sub']})")

        if not user or not user.is_active:
            raise UnauthorizedException("User not found or deactivated.")

        perf_total_elapsed = time.perf_counter() - perf_total_start
        logger.debug(f"[PERF] AUTH SERVICE TOTAL: {perf_total_elapsed:.3f}s")

        return user