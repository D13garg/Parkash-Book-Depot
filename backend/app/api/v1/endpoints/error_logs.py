from typing import Optional
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_admin
from app.services.error_log_service import ErrorLogService
from app.schemas.error_log import ErrorLogResponse
from app.schemas.book import PaginatedResponse
from app.models.user import UserModel

router = APIRouter()


@router.get("", response_model=PaginatedResponse[ErrorLogResponse])
async def get_error_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    level: Optional[str] = Query(default=None),
    endpoint: Optional[str] = Query(default=None),
    from_date: Optional[datetime] = Query(default=None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: UserModel = Depends(get_current_admin),
):
    """Admin only. Returns last 7 days of error logs — older ones auto-deleted by MongoDB TTL."""
    service = ErrorLogService(db)
    return await service.get_logs(
        page=page, page_size=page_size,
        level=level, endpoint=endpoint, from_date=from_date,
    )