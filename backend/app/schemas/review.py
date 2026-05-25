from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class ReviewCreate(BaseModel):
    reviewer_name: str
    reviewer_email: EmailStr

    rating: int = Field(..., ge=1, le=5)

    review_type: str
    message: str


class ReviewResponse(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")

    reviewer_name: str
    reviewer_email: EmailStr

    rating: int
    review_type: str
    message: str

    created_at: datetime

    class Config:
        populate_by_name = True