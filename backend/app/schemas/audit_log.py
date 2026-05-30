from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class AuditLogResponse(BaseModel):
    id: str
    actor_id: str
    actor_name: str
    actor_role: str
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    description: str
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime