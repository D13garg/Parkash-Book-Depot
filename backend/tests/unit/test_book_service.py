import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.book_service import BookService
from app.schemas.book import CreateBookRequest, UpdateBookRequest
from app.core.exceptions import NotFoundException
from app.core.enums import UserRole
from tests.conftest import make_user, make_book


def _admin():
    return make_user(id="admin1", role=UserRole.ADMIN)


class TestCreateBook:
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    async def test_create_book_success(self, mock_db):
        book = make_book()
        with patch("app.services.book_service.BookRepository") as R, \
             patch("app.services.book_service.audit"), \
             patch("app.services.book_service.inc_metric"):
            R.return_value.create = AsyncMock(return_value=book)
            result = await BookService(mock_db).create_book(
                CreateBookRequest(title="Test Book", authors=["Author"],
                                  categories=["textbook"], price=299.0, stock=10),
                _admin()
            )
        assert result.title == "Test Book"
        assert result.stock == 10

    async def test_create_book_low_stock_flag(self, mock_db):
        book = make_book(stock=3)  # below threshold of 5
        with patch("app.services.book_service.BookRepository") as R, \
             patch("app.services.book_service.audit"), \
             patch("app.services.book_service.inc_metric"):
            R.return_value.create = AsyncMock(return_value=book)
            result = await BookService(mock_db).create_book(
                CreateBookRequest(title="Test Book", authors=["Author"],
                                  categories=["textbook"], price=299.0, stock=3),
                _admin()
            )
        assert result.is_low_stock is True

    async def test_create_book_adequate_stock_not_low(self, mock_db):
        book = make_book(stock=10)
        with patch("app.services.book_service.BookRepository") as R, \
             patch("app.services.book_service.audit"), \
             patch("app.services.book_service.inc_metric"):
            R.return_value.create = AsyncMock(return_value=book)
            result = await BookService(mock_db).create_book(
                CreateBookRequest(title="Test Book", authors=["Author"],
                                  categories=["textbook"], price=299.0, stock=10),
                _admin()
            )
        assert result.is_low_stock is False


class TestGetBook:
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    async def test_get_book_found(self, mock_db):
        book = make_book()
        with patch("app.services.book_service.BookRepository") as R:
            R.return_value.find_by_id = AsyncMock(return_value=book)
            result = await BookService(mock_db).get_book("book123")
        assert result.id == "book123"

    async def test_get_book_not_found_raises(self, mock_db):
        with patch("app.services.book_service.BookRepository") as R:
            R.return_value.find_by_id = AsyncMock(return_value=None)
            with pytest.raises(NotFoundException):
                await BookService(mock_db).get_book("nonexistent")


class TestUpdateStock:
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    async def test_update_stock_success(self, mock_db):
        book = make_book(stock=10)
        updated_book = make_book(stock=25)
        with patch("app.services.book_service.BookRepository") as R, \
             patch("app.services.book_service.audit"), \
             patch("app.services.book_service.inc_metric"):
            R.return_value.find_by_id = AsyncMock(return_value=book)
            R.return_value.update_stock = AsyncMock(return_value=updated_book)
            result = await BookService(mock_db).update_stock("book123", 25, _admin())
        assert result.stock == 25

    async def test_update_stock_book_not_found_raises(self, mock_db):
        with patch("app.services.book_service.BookRepository") as R, \
             patch("app.services.book_service.audit"), \
             patch("app.services.book_service.inc_metric"):
            R.return_value.find_by_id = AsyncMock(return_value=None)
            with pytest.raises(NotFoundException):
                await BookService(mock_db).update_stock("bad_id", 10, _admin())


class TestDeleteBook:
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    async def test_delete_book_success(self, mock_db):
        book = make_book()
        with patch("app.services.book_service.BookRepository") as R, \
             patch("app.services.book_service.audit"), \
             patch("app.services.book_service.inc_metric"):
            R.return_value.find_by_id = AsyncMock(return_value=book)
            R.return_value.soft_delete = AsyncMock(return_value=True)
            result = await BookService(mock_db).delete_book("book123", _admin())
        assert "deleted" in result["message"].lower()

    async def test_delete_book_not_found_raises(self, mock_db):
        with patch("app.services.book_service.BookRepository") as R, \
             patch("app.services.book_service.audit"), \
             patch("app.services.book_service.inc_metric"):
            R.return_value.find_by_id = AsyncMock(return_value=None)
            with pytest.raises(NotFoundException):
                await BookService(mock_db).delete_book("bad_id", _admin())