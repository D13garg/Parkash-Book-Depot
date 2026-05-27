from datetime import datetime, timedelta, timezone
from typing import Optional
import hmac
import hashlib
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

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