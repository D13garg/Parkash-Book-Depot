from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from app.core.enums import ProjectRequestStatus


class CreateProjectRequestRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    category: str = Field(..., min_length=2)
    request_type: Literal["project", "other"] = "project"
    requirements: Optional[str] = None
    quantity: Optional[int] = Field(default=None, gt=0)
    institution_name: Optional[str] = None
    institution_address: Optional[str] = None
    contact_phone: Optional[str] = None


class UpdateRequestStatusRequest(BaseModel):
    status: ProjectRequestStatus
    admin_notes: Optional[str] = None
    rejection_reason: Optional[str] = None


class ProjectRequestResponse(BaseModel):
    id: str
    customer_id: str
    title: str
    description: str
    category: str
    request_type: str
    requirements: Optional[str] = None
    quantity: Optional[int] = None
    institution_name: Optional[str] = None
    institution_address: Optional[str] = None
    contact_phone: Optional[str] = None
    status: ProjectRequestStatus
    admin_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime