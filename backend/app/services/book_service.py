import math
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from app.repositories.book_repository import BookRepository
from app.schemas.book import CreateBookRequest, UpdateBookRequest, BookResponse, PaginatedResponse
from app.models.book import BookModel
from app.models.user import UserModel
from app.core.exceptions import NotFoundException
from app.services.audit_log_service import audit
from app.services.metrics_service import increment as inc_metric


def _to_book_response(book: BookModel) -> BookResponse:
    return BookResponse(
        id=book.id, title=book.title, authors=book.authors,
        categories=book.categories, price=book.price, stock=book.stock,
        low_stock_threshold=book.low_stock_threshold,
        is_low_stock=book.stock < book.low_stock_threshold,
        publisher=book.publisher, isbn=book.isbn, description=book.description,
        cover_image_url=book.cover_image_url, edition=book.edition,
        language=book.language, is_active=book.is_active,
        created_at=book.created_at, updated_at=book.updated_at,
    )


class BookService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.book_repo = BookRepository(db)
        self.db = db

    async def get_books(self, *, page=1, page_size=20, category=None, author=None,
                        min_price=None, max_price=None, in_stock_only=False, search=None):
        skip = (page - 1) * page_size
        books, total = await self.book_repo.find_many(
            category=category, author=author, min_price=min_price,
            max_price=max_price, in_stock_only=in_stock_only,
            search=search, skip=skip, limit=page_size,
        )
        return PaginatedResponse(
            items=[_to_book_response(b) for b in books], total=total,
            page=page, page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 1,
        )

    async def get_book(self, book_id: str) -> BookResponse:
        book = await self.book_repo.find_by_id(book_id)
        if not book:
            raise NotFoundException("Book")
        return _to_book_response(book)

    async def create_book(self, data: CreateBookRequest, current_user: UserModel) -> BookResponse:
        book = await self.book_repo.create(data.model_dump())
        await audit(
            db=self.db, actor_id=current_user.id, actor_name=current_user.name,
            actor_role=current_user.role, action="book_created",
            description=f"Book added: \"{book.title}\"",
            entity_type="book", entity_id=book.id,
            metadata={"title": book.title, "price": book.price, "stock": book.stock},
        )
        await inc_metric(self.db, "books_added")
        return _to_book_response(book)

    async def update_book(self, book_id: str, data: UpdateBookRequest, current_user: UserModel) -> BookResponse:
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            return await self.get_book(book_id)
        book = await self.book_repo.update(book_id, update_data)
        if not book:
            raise NotFoundException("Book")
        await audit(
            db=self.db, actor_id=current_user.id, actor_name=current_user.name,
            actor_role=current_user.role, action="book_updated",
            description=f"Book updated: \"{book.title}\"",
            entity_type="book", entity_id=book_id,
            metadata={"updated_fields": list(update_data.keys())},
        )
        return _to_book_response(book)

    async def delete_book(self, book_id: str, current_user: UserModel) -> dict:
        book = await self.book_repo.find_by_id(book_id)
        if not book:
            raise NotFoundException("Book")
        await self.book_repo.soft_delete(book_id)
        await audit(
            db=self.db, actor_id=current_user.id, actor_name=current_user.name,
            actor_role=current_user.role, action="book_deleted",
            description=f"Book deleted: \"{book.title}\"",
            entity_type="book", entity_id=book_id,
        )
        return {"message": "Book deleted successfully."}

    async def update_stock(self, book_id: str, new_stock: int, current_user: UserModel) -> BookResponse:
        book = await self.book_repo.find_by_id(book_id)
        if not book:
            raise NotFoundException("Book")
        old_stock = book.stock
        updated = await self.book_repo.update_stock(book_id, new_stock)
        await audit(
            db=self.db, actor_id=current_user.id, actor_name=current_user.name,
            actor_role=current_user.role, action="book_stock_updated",
            description=f"Stock updated for \"{book.title}\": {old_stock} → {new_stock}",
            entity_type="book", entity_id=book_id,
            metadata={"old_stock": old_stock, "new_stock": new_stock},
        )
        return _to_book_response(updated)

    async def get_low_stock_books(self) -> list[BookResponse]:
        books = await self.book_repo.find_low_stock()
        return [_to_book_response(b) for b in books]