from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.core.enums import UserRole


# ── Request schemas (what the API accepts) ────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    phone: Optional[str] = None
    address: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ── Response schemas (what the API returns) ───────────────────────────────────

class UserResponse(BaseModel):
    """Safe user representation — never includes hashed_password."""
    id: str
    name: str
    email: str
    role: UserRole
    is_active: bool
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class AccessTokenResponse(BaseModel):
    """Returned by the /refresh endpoint — only a new access token."""
    access_token: str
    token_type: str = "bearer"
