from fastapi import APIRouter, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.services.auth_service import AuthService
from app.schemas.user import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    AccessTokenResponse,
    UserResponse,
)
from app.models.user import UserModel
from app.middleware.rate_limit import limiter

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit("5/minute")
async def register(
    request: Request,
    data: RegisterRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Register a new customer account.
    Rate limited: 5 registrations per minute per IP.
    """
    service = AuthService(db)
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    data: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Login with email and password.
    Rate limited: 10 attempts per minute per IP.
    """
    service = AuthService(db)
    return await service.login(data)


@router.post("/refresh", response_model=AccessTokenResponse)
@limiter.limit("20/minute")
async def refresh_token(
    request: Request,
    data: RefreshTokenRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Exchange a valid refresh token for a new access token.
    Rate limited: 20 per minute per IP.
    """
    service = AuthService(db)
    return await service.refresh(data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: UserModel = Depends(get_current_user),
):
    """Returns the currently authenticated user's profile."""
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