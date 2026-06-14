from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CreateReviewRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    category: str = Field(..., min_length=1)
    message: str = Field(..., min_length=5)


class UpdateReviewRequest(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    category: Optional[str] = Field(default=None, min_length=1)
    message: Optional[str] = Field(default=None, min_length=5)


class ReviewResponse(BaseModel):
    id: str
    customer_id: str
    customer_name: str
    rating: int
    category: str
    message: str
    created_at: datetime
    updated_at: Optional[datetime] = None