from pydantic import BaseModel, Field
from typing import Optional, List, Generic, TypeVar
from datetime import datetime

T = TypeVar("T")


# ── Request schemas ────────────────────────────────────────────────────────────

class CreateBookRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    authors: List[str] = Field(..., min_length=1)
    categories: List[str] = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    edition: Optional[str] = None
    language: str = "English"
    low_stock_threshold: int = Field(default=5, ge=0)


class UpdateBookRequest(BaseModel):
    """All fields optional — only provided fields are updated."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=300)
    authors: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    price: Optional[float] = Field(default=None, gt=0)
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    edition: Optional[str] = None
    language: Optional[str] = None
    low_stock_threshold: Optional[int] = Field(default=None, ge=0)
    stock: Optional[int] = Field(default=None, ge=0)


class UpdateStockRequest(BaseModel):
    """Used by PATCH /books/{id}/stock"""
    stock: int = Field(..., ge=0)


# ── Response schemas ───────────────────────────────────────────────────────────

class BookResponse(BaseModel):
    id: str
    title: str
    authors: List[str]
    categories: List[str]
    price: float
    stock: int
    low_stock_threshold: int
    is_low_stock: bool          # computed field — True if stock < low_stock_threshold
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    edition: Optional[str] = None
    language: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated wrapper used for any list endpoint.
    Usage: PaginatedResponse[BookResponse]
    """
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
