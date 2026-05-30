from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.audit_log import AuditLogResponse
from app.schemas.book import PaginatedResponse
from datetime import datetime
import math


async def audit(
    db: AsyncIOMotorDatabase,
    actor_id: str,
    actor_name: str,
    actor_role: str,
    action: str,
    description: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> None:
    """Silent audit logger — never raises, never breaks main action."""
    try:
        repo = AuditLogRepository(db)
        await repo.create({
            "actor_id": actor_id,
            "actor_name": actor_name,
            "actor_role": actor_role,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "description": description,
            "metadata": metadata,
            "ip_address": ip_address,
        })
    except Exception:
        pass


def _to_response(log) -> AuditLogResponse:
    return AuditLogResponse(
        id=log.id,
        actor_id=log.actor_id,
        actor_name=log.actor_name,
        actor_role=log.actor_role,
        action=log.action,
        entity_type=log.entity_type,
        entity_id=log.entity_id,
        description=log.description,
        metadata=log.metadata,
        ip_address=log.ip_address,
        created_at=log.created_at,
    )


class AuditLogService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = AuditLogRepository(db)

    async def get_logs(
        self,
        page: int = 1,
        page_size: int = 50,
        action: Optional[str] = None,
        actor_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
    ) -> PaginatedResponse[AuditLogResponse]:
        skip = (page - 1) * page_size
        logs, total = await self.repo.find_all(
            action=action, actor_id=actor_id,
            entity_type=entity_type, from_date=from_date,
            skip=skip, limit=page_size,
        )
        return PaginatedResponse(
            items=[_to_response(l) for l in logs],
            total=total, page=page, page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 1,
        )

    async def get_entity_logs(self, entity_type: str, entity_id: str) -> list[AuditLogResponse]:
        logs = await self.repo.find_by_entity(entity_type, entity_id)
        return [_to_response(l) for l in logs]