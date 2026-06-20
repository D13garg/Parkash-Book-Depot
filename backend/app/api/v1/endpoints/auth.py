from fastapi import APIRouter, Depends, Request, Response
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.core.security import (
    ACCESS_TOKEN_COOKIE,
    REFRESH_TOKEN_COOKIE,
    CSRF_TOKEN_COOKIE,
    CSRF_TOKEN_HEADER,
    generate_csrf_token,
    set_auth_cookies,
    set_access_token_cookie,
    clear_auth_cookies,
    decode_token,
)
from app.core.exceptions import UnauthorizedException
from app.schemas.user import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    AccessTokenResponse,
    UserResponse,
    RegisterInitiateRequest,
    OTPVerifyRequest,
    OTPInitiateResponse,
    ForgotPasswordInitiateRequest,
    ForgotPasswordVerifyRequest,
    MessageResponse,
    GoogleAuthRequest,
)
from app.models.user import UserModel
from app.middleware.rate_limit import limiter

router = APIRouter()


# ── Registration (2-step: initiate → verify OTP) ─────────────────────────────

@router.post("/register/initiate", response_model=OTPInitiateResponse, status_code=200)
@limiter.limit("5/minute")
async def register_initiate(
    request: Request,
    data: RegisterInitiateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Step 1: Validate registration data and send OTP to email.
    Rate limited: 5/minute per IP. OTP service further limits to 3 sends/hour per email.
    """
    service = AuthService(db)
    return await service.register_initiate(data)


@router.post("/register/verify", response_model=TokenResponse, status_code=201)
@limiter.limit("10/minute")
async def register_verify(
    request: Request,
    response: Response,
    data: OTPVerifyRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Step 2: Verify OTP → create account → return tokens.
    OTP expires in 3 minutes and is single-use.
    Rate limited: 10/minute per IP. OTP service limits to 5 wrong attempts before lockout.
    """
    service = AuthService(db)
    result = await service.register_verify(data)
    set_auth_cookies(
        response,
        result.access_token,
        result.refresh_token,
        generate_csrf_token(),
    )
    return result


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    response: Response,
    data: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Login with email and password."""
    service = AuthService(db)
    result = await service.login(data)
    set_auth_cookies(
        response,
        result.access_token,
        result.refresh_token,
        generate_csrf_token(),
    )
    return result


# ── Forgot password (2-step: initiate → verify OTP + new password) ────────────

@router.post("/forgot-password/initiate", response_model=MessageResponse, status_code=200)
@limiter.limit("5/minute")
async def forgot_password_initiate(
    request: Request,
    data: ForgotPasswordInitiateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Send OTP to email for password reset.
    Always returns 200 regardless of whether email exists — prevents enumeration.
    Rate limited: 5/minute per IP.
    """
    service = AuthService(db)
    await service.forgot_password_initiate(data.email)
    return MessageResponse(
        message="If that email is registered, a verification code has been sent."
    )


@router.post("/forgot-password/verify", response_model=MessageResponse, status_code=200)
@limiter.limit("10/minute")
async def forgot_password_verify(
    request: Request,
    data: ForgotPasswordVerifyRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Verify OTP and reset password.
    Rate limited: 10/minute per IP. OTP service limits to 5 wrong attempts.
    """
    service = AuthService(db)
    await service.forgot_password_verify(data)
    return MessageResponse(message="Password reset successfully. You can now sign in.")


# ── Google OAuth ──────────────────────────────────────────────────────────────

@router.post("/google", response_model=TokenResponse, status_code=200)
@limiter.limit("10/minute")
async def google_auth(
    request: Request,
    response: Response,
    data: GoogleAuthRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Authenticate with a Google ID token.
    Verifies token with Google's tokeninfo endpoint.
    Creates account on first login, finds existing on subsequent logins.
    """
    service = AuthService(db)
    result = await service.google_auth(data)
    set_auth_cookies(
        response,
        result.access_token,
        result.refresh_token,
        generate_csrf_token(),
    )
    return result


# ── Token refresh ─────────────────────────────────────────────────────────────

@router.post("/refresh", response_model=AccessTokenResponse)
@limiter.limit("20/minute")
async def refresh_token(
    request: Request,
    response: Response,
    data: RefreshTokenRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Exchange a valid refresh token for a new access token."""
    refresh = request.cookies.get(REFRESH_TOKEN_COOKIE) or data.refresh_token
    if not refresh:
        raise UnauthorizedException("Refresh token required.")

    service = AuthService(db)
    result = await service.refresh(refresh)
    set_access_token_cookie(response, result.access_token)
    return result


@router.post("/logout", response_model=MessageResponse)
async def logout(request: Request, response: Response, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Clear auth cookies and revoke the refresh token server-side.

    Previously this only cleared cookies — a copied-out refresh token (e.g.
    stolen from a compromised device, or just lifted from browser storage
    before the user logged out) would keep working for its full lifetime
    regardless of logout. Bumping token_version closes that gap.

    Deliberately tolerant of a missing/expired/invalid access token: logout
    should never fail just because the session was already stale — cookies
    still get cleared either way, and we only attempt the revocation if we
    can identify who to revoke for.

    Reads the access token from the cookie only, not a Bearer header — this
    endpoint is for browser sessions. The CLI and MCP server authenticate via
    Bearer token directly and don't go through a cookie-based login/logout
    flow at all, so they're unaffected by this endpoint either way.
    """
    token = request.cookies.get(ACCESS_TOKEN_COOKIE)
    if token:
        payload = decode_token(token)
        if payload and payload.get("sub"):
            try:
                await UserRepository(db).bump_token_version(payload["sub"])
            except Exception:
                pass  # logout must still succeed even if revocation lookup fails
    clear_auth_cookies(response)
    return MessageResponse(message="Logged out successfully.")


# ── Current user ──────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserResponse)
async def get_me(
    request: Request,
    response: Response,
    current_user: UserModel = Depends(get_current_user),
):
    """Returns the currently authenticated user's profile."""
    csrf = request.cookies.get(CSRF_TOKEN_COOKIE)
    if csrf:
        response.headers[CSRF_TOKEN_HEADER] = csrf
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        phone=current_user.phone,
        address=current_user.address,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )