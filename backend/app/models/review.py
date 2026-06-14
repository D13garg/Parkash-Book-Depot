from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional


class ReviewModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    customer_id: str                        # who submitted it
    customer_name: str                      # denormalised for admin view
    rating: int = Field(..., ge=1, le=5)
    category: str                           # overall | service | delivery | quality
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True