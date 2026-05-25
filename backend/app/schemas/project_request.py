from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.core.enums import ProjectRequestStatus


# ── Request schemas ────────────────────────────────────────────────────────────

class CreateProjectRequestRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    category: str = Field(..., min_length=2)
    requirements: Optional[str] = None
    quantity: Optional[int] = Field(default=None, gt=0)
    institution_name: Optional[str] = None
    institution_address: Optional[str] = None
    contact_phone: Optional[str] = None


class UpdateRequestStatusRequest(BaseModel):
    """Used by admin to move a request through the workflow."""
    status: ProjectRequestStatus
    admin_notes: Optional[str] = None
    rejection_reason: Optional[str] = None     # required when rejecting


# ── Response schemas ───────────────────────────────────────────────────────────

class ProjectRequestResponse(BaseModel):
    id: str
    customer_id: str
    title: str
    description: str
    category: str
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
