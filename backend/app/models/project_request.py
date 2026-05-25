from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.core.enums import ProjectRequestStatus


class ProjectRequestModel(BaseModel):
    """
    Represents a customer-submitted project request in MongoDB.
    """
    id: Optional[str] = Field(default=None, alias="_id")
    customer_id: str                            # references users._id
    title: str
    description: str
    category: str                               # e.g. "bulk_order", "institutional", "custom"
    requirements: Optional[str] = None         # detailed requirements text
    quantity: Optional[int] = None             # number of books/items requested
    institution_name: Optional[str] = None     # school, college, library name
    institution_address: Optional[str] = None
    contact_phone: Optional[str] = None
    status: ProjectRequestStatus = ProjectRequestStatus.SUBMITTED
    admin_notes: Optional[str] = None          # internal notes added by admin
    rejection_reason: Optional[str] = None     # filled if rejected
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
