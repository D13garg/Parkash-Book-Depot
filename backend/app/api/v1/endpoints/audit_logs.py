from typing import Optional
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_admin
from app.services.audit_log_service import AuditLogService
from app.schemas.audit_log import AuditLogResponse
from app.schemas.book import PaginatedResponse
from app.models.user import UserModel

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AuditLogResponse])
async def get_audit_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    action: Optional[str] = Query(default=None),
    actor_id: Optional[str] = Query(default=None),
    entity_type: Optional[str] = Query(default=None),
    from_date: Optional[datetime] = Query(default=None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: UserModel = Depends(get_current_admin),
):
    service = AuditLogService(db)
    return await service.get_logs(
        page=page, page_size=page_size, action=action,
        actor_id=actor_id, entity_type=entity_type, from_date=from_date,
    )


@router.get("/entity/{entity_type}/{entity_id}", response_model=list[AuditLogResponse])
async def get_entity_logs(
    entity_type: str,
    entity_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: UserModel = Depends(get_current_admin),
):
    service = AuditLogService(db)
    return await service.get_entity_logs(entity_type, entity_id)