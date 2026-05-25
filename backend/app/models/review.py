from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone
from typing import Optional


class ReviewModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")

    reviewer_name: str
    reviewer_email: EmailStr

    rating: int = Field(..., ge=1, le=5)

    review_type: str
    message: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Config:
        populate_by_name = True