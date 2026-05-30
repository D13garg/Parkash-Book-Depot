from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ErrorLogResponse(BaseModel):
    id: str
    level: str
    endpoint: Optional[str] = None
    method: Optional[str] = None
    message: str
    stack_trace: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    status_code: Optional[int] = None
    created_at: datetime