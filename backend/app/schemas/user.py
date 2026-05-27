from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from app.core.enums import UserRole


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    phone: Optional[str] = None
    address: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        from app.core.security import validate_password_strength
        error = validate_password_strength(v)
        if error:
            raise ValueError(error)
        return v

    @field_validator("email")
    @classmethod
    def email_must_be_real(cls, v: str) -> str:
        from app.core.email_validation import validate_email_quality
        error = validate_email_quality(v)
        if error:
            raise ValueError(error)
        return v

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        if not any(c.isalpha() for c in v):
            raise ValueError("Name must contain at least some letters.")
        return v.strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
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
    access_token: str
    token_type: str = "bearer"