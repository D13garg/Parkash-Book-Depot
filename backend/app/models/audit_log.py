from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timezone


class AuditLogModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    actor_id: str
    actor_name: str
    actor_role: str
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    description: str
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True