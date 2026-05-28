from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone


class BookModel(BaseModel):
    """
    Represents a book document stored in MongoDB.
    Flexible + resilient production-ready schema.
    """

    id: Optional[str] = Field(default=None, alias="_id")

    # Core identity
    title: str

    # Collections
    authors: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)

    # Metadata
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    edition: Optional[str] = None
    language: str = "English"

    # Inventory / business
    price: float = 0.0
    stock: int = 0
    low_stock_threshold: int = 5

    # Media
    cover_image_url: Optional[str] = None

    # Status
    is_active: bool = True

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Config:
        populate_by_name = True

        # Ignore unexpected MongoDB fields safely
        extra = "ignore"