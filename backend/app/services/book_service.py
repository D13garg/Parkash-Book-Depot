import math
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.repositories.book_repository import BookRepository
from app.schemas.book import (
    CreateBookRequest,
    UpdateBookRequest,
    BookResponse,
    PaginatedResponse,
)
from app.models.book import BookModel
from app.core.exceptions import NotFoundException


def _to_book_response(book: BookModel) -> BookResponse:
    """Convert BookModel to BookResponse, computing is_low_stock."""
    return BookResponse(
        id=book.id,
        title=book.title,
        authors=book.authors,
        categories=book.categories,
        price=book.price,
        stock=book.stock,
        is_low_stock=book.stock < book.low_stock_threshold,
        publisher=book.publisher,
        isbn=book.isbn,
        description=book.description,
        cover_image_url=book.cover_image_url,
        edition=book.edition,
        language=book.language,
        is_active=book.is_active,
        created_at=book.created_at,
        updated_at=book.updated_at,
    )


class BookService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.book_repo = BookRepository(db)

    async def get_books(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        author: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock_only: bool = False,
        search: Optional[str] = None,
    ) -> PaginatedResponse[BookResponse]:
        skip = (page - 1) * page_size
        books, total = await self.book_repo.find_many(
            category=category,
            author=author,
            min_price=min_price,
            max_price=max_price,
            in_stock_only=in_stock_only,
            search=search,
            skip=skip,
            limit=page_size,
        )
        return PaginatedResponse(
            items=[_to_book_response(b) for b in books],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 1,
        )

    async def get_book(self, book_id: str) -> BookResponse:
        book = await self.book_repo.find_by_id(book_id)
        if not book:
            raise NotFoundException("Book")
        return _to_book_response(book)

    async def create_book(self, data: CreateBookRequest) -> BookResponse:
        book_doc = data.model_dump()
        book = await self.book_repo.create(book_doc)
        return _to_book_response(book)

    async def update_book(self, book_id: str, data: UpdateBookRequest) -> BookResponse:
        # Only include fields that were actually provided
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            # Nothing to update — just return current state
            return await self.get_book(book_id)

        book = await self.book_repo.update(book_id, update_data)
        if not book:
            raise NotFoundException("Book")
        return _to_book_response(book)

    async def delete_book(self, book_id: str) -> dict:
        deleted = await self.book_repo.soft_delete(book_id)
        if not deleted:
            raise NotFoundException("Book")
        return {"message": "Book deleted successfully."}

    async def update_stock(self, book_id: str, new_stock: int) -> BookResponse:
        book = await self.book_repo.update_stock(book_id, new_stock)
        if not book:
            raise NotFoundException("Book")
        return _to_book_response(book)

    async def get_low_stock_books(self) -> list[BookResponse]:
        books = await self.book_repo.find_low_stock()
        return [_to_book_response(b) for b in books]
