from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.core.enums import ProjectStatus


class ProjectModel(BaseModel):
    """
    Represents an internal operational project in MongoDB.
    Always linked back to the customer request that created it.
    """
    id: Optional[str] = Field(default=None, alias="_id")
    request_id: str                         # references project_requests._id
    created_by: str                         # admin user id who created this project
    assigned_to: Optional[str] = None       # associate user id — None until assigned
    title: str
    description: str
    priority: str = "medium"                # low | medium | high | urgent
    deadline: Optional[datetime] = None
    status: ProjectStatus = ProjectStatus.PENDING
    notes: Optional[str] = None             # internal admin notes
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
