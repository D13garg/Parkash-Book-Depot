from fastapi import APIRouter, Depends, Query
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_admin
from app.services.book_service import BookService
from app.schemas.book import (
    CreateBookRequest,
    UpdateBookRequest,
    UpdateStockRequest,
    BookResponse,
    PaginatedResponse,
)
from app.models.user import UserModel

router = APIRouter()


# ── Public routes (no login required) ─────────────────────────────────────────

@router.get("", response_model=PaginatedResponse[BookResponse])
async def list_books(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: Optional[str] = Query(default=None),
    author: Optional[str] = Query(default=None),
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    in_stock_only: bool = Query(default=False),
    search: Optional[str] = Query(default=None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Browse books with optional filters.
    Public endpoint — no authentication required.
    """
    service = BookService(db)
    return await service.get_books(
        page=page,
        page_size=page_size,
        category=category,
        author=author,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock_only,
        search=search,
    )


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get a single book by ID. Public endpoint."""
    service = BookService(db)
    return await service.get_book(book_id)


# ── Admin-only routes ──────────────────────────────────────────────────────────

@router.post("", response_model=BookResponse, status_code=201)
async def create_book(
    data: CreateBookRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: UserModel = Depends(get_current_admin),   # enforces admin role
):
    """Add a new book. Admin only."""
    service = BookService(db)
    return await service.create_book(data)


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: str,
    data: UpdateBookRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: UserModel = Depends(get_current_admin),
):
    """Update book details. Admin only."""
    service = BookService(db)
    return await service.update_book(book_id, data)


@router.delete("/{book_id}")
async def delete_book(
    book_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: UserModel = Depends(get_current_admin),
):
    """Soft-delete a book (marks inactive, not removed from DB). Admin only."""
    service = BookService(db)
    return await service.delete_book(book_id)


@router.patch("/{book_id}/stock", response_model=BookResponse)
async def update_stock(
    book_id: str,
    data: UpdateStockRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: UserModel = Depends(get_current_admin),
):
    """Update stock quantity for a book. Admin only."""
    service = BookService(db)
    return await service.update_stock(book_id, data.stock)


@router.get("/admin/low-stock", response_model=list[BookResponse])
async def get_low_stock(
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: UserModel = Depends(get_current_admin),
):
    """Returns all books where stock is below their low_stock_threshold. Admin only."""
    service = BookService(db)
    return await service.get_low_stock_books()
