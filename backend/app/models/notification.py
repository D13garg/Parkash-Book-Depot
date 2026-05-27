from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


class NotificationModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str                        # who receives this notification
    type: str                           # request_submitted | review_submitted | project_assigned
    message: str
    link: Optional[str] = None          # frontend route to navigate on click
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True