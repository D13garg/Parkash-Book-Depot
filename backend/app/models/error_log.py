from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


class ErrorLogModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    level: str = "ERROR"               # ERROR | WARNING
    endpoint: Optional[str] = None
    method: Optional[str] = None
    message: str
    stack_trace: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    status_code: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True