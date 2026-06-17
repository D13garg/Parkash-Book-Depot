from datetime import datetime, timedelta, timezone
from typing import Optional
import hmac
import hashlib
import secrets
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Response
from app.core.config import settings

# Cookie names shared by auth endpoints and the auth dependency
ACCESS_TOKEN_COOKIE = "access_token"
REFRESH_TOKEN_COOKIE = "refresh_token"
CSRF_TOKEN_COOKIE = "csrf_token"
CSRF_TOKEN_HEADER = "X-CSRF-Token"
REFRESH_TOKEN_COOKIE_PATH = f"{settings.API_V1_PREFIX}/auth/refresh"

# bcrypt handles salt automatically — we add pepper before bcrypt sees the password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Pepper ────────────────────────────────────────────────────────────────────

def _apply_pepper(plain_password: str) -> str:
    """
    Mix the server-side PEPPER into the password using HMAC-SHA256
    before passing to bcrypt.

    Why this matters:
    - bcrypt auto-salt protects against rainbow tables
    - pepper protects against offline brute force if DB is dumped
    - Even with the full database, attacker needs PEPPER (server secret)
      to crack any password

    IMPORTANT: Never change PEPPER after users have registered.
    If changed, all existing passwords become unverifiable.
    """
    return hmac.new(
        settings.PEPPER.encode("utf-8"),
        plain_password.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """Pepper the password then hash with bcrypt (bcrypt adds its own salt)."""
    peppered = _apply_pepper(plain_password)
    return pwd_context.hash(peppered)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Pepper the password then verify against the stored bcrypt hash."""
    peppered = _apply_pepper(plain_password)
    return pwd_context.verify(peppered, hashed_password)


def validate_password_strength(password: str) -> Optional[str]:
    """
    Returns an error message if password is too weak, None if fine.
    """
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if not any(c.isupper() for c in password):
        return "Password must contain at least one uppercase letter."
    if not any(c.islower() for c in password):
        return "Password must contain at least one lowercase letter."
    if not any(c.isdigit() for c in password):
        return "Password must contain at least one number."
    if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password):
        return "Password must contain at least one special character (!@#$%^&* etc)."
    return None


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT. Returns payload dict or None on failure."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


# ── CSRF + auth cookie helpers ────────────────────────────────────────────────

def generate_csrf_token() -> str:
    """Random hex token for double-submit CSRF protection."""
    return secrets.token_hex(32)


def _cross_origin_cookie_params(*, httponly: bool) -> dict:
    """
    Production (Vercel → Railway): SameSite=None + Secure for cross-origin cookies.
    Development (localhost HTTP): lax + non-secure so cookies work without HTTPS.
    """
    is_production = settings.ENVIRONMENT == "production"
    return {
        "httponly": httponly,
        "secure": is_production,
        "samesite": "none" if is_production else "lax",
    }


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    csrf_token: str,
) -> None:
    """Set httpOnly JWT cookies plus a readable CSRF cookie after login/register/google."""
    common = _cross_origin_cookie_params(httponly=True)
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        path="/",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **common,
    )
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        path=REFRESH_TOKEN_COOKIE_PATH,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        **common,
    )
    response.set_cookie(
        key=CSRF_TOKEN_COOKIE,
        value=csrf_token,
        path="/",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        **_cross_origin_cookie_params(httponly=False),
    )
    # Cross-origin frontends cannot read API-domain cookies — echo token in header
    response.headers[CSRF_TOKEN_HEADER] = csrf_token


def set_access_token_cookie(response: Response, access_token: str) -> None:
    """Update only the access token cookie after a refresh."""
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        path="/",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **_cross_origin_cookie_params(httponly=True),
    )


def clear_auth_cookies(response: Response) -> None:
    """Expire all auth-related cookies on logout."""
    common = _cross_origin_cookie_params(httponly=True)
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE, value="", max_age=0, path="/", **common
    )
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value="",
        max_age=0,
        path=REFRESH_TOKEN_COOKIE_PATH,
        **common,
    )
    response.set_cookie(
        key=CSRF_TOKEN_COOKIE,
        value="",
        max_age=0,
        path="/",
        **_cross_origin_cookie_params(httponly=False),
    )