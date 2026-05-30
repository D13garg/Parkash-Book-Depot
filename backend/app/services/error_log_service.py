import traceback
import math
from typing import Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.error_log_repository import ErrorLogRepository
from app.schemas.error_log import ErrorLogResponse
from app.schemas.book import PaginatedResponse


async def log_error(
    db: AsyncIOMotorDatabase,
    message: str,
    level: str = "ERROR",
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
    stack_trace: Optional[str] = None,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    status_code: Optional[int] = None,
) -> None:
    """Silent error logger — never raises."""
    try:
        repo = ErrorLogRepository(db)
        await repo.create({
            "level": level,
            "endpoint": endpoint,
            "method": method,
            "message": message,
            "stack_trace": stack_trace,
            "user_id": user_id,
            "ip_address": ip_address,
            "status_code": status_code,
        })
    except Exception:
        pass


def _to_response(log) -> ErrorLogResponse:
    return ErrorLogResponse(
        id=log.id, level=log.level, endpoint=log.endpoint,
        method=log.method, message=log.message,
        stack_trace=log.stack_trace, user_id=log.user_id,
        ip_address=log.ip_address, status_code=log.status_code,
        created_at=log.created_at,
    )


class ErrorLogService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = ErrorLogRepository(db)

    async def get_logs(
        self,
        page: int = 1,
        page_size: int = 50,
        level: Optional[str] = None,
        endpoint: Optional[str] = None,
        from_date: Optional[datetime] = None,
    ) -> PaginatedResponse[ErrorLogResponse]:
        skip = (page - 1) * page_size
        logs, total = await self.repo.find_all(
            level=level, endpoint=endpoint,
            from_date=from_date, skip=skip, limit=page_size,
        )
        return PaginatedResponse(
            items=[_to_response(l) for l in logs],
            total=total, page=page, page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 1,
        )