from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.core.enums import ProjectRequestStatus


class ProjectRequestModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    customer_id: str
    title: str
    description: str
    category: str
    request_type: str = "project"       # "project" | "other"
    requirements: Optional[str] = None
    quantity: Optional[int] = None
    institution_name: Optional[str] = None
    institution_address: Optional[str] = None
    contact_phone: Optional[str] = None
    status: ProjectRequestStatus = ProjectRequestStatus.SUBMITTED
    admin_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True