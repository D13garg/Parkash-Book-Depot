from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone


class BookModel(BaseModel):
    """
    Represents a book document as stored in MongoDB.
    """
    id: Optional[str] = Field(default=None, alias="_id")
    title: str
    authors: List[str]
    categories: List[str]
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    price: float
    stock: int = 0
    low_stock_threshold: int = 5       # alert when stock drops below this
    cover_image_url: Optional[str] = None
    edition: Optional[str] = None
    language: str = "English"
    is_active: bool = True             # soft delete — hide without removing
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
