import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.review_service import ReviewService
from app.schemas.review import CreateReviewRequest
from app.core.enums import UserRole
from app.core.exceptions import ForbiddenException
from tests.conftest import make_user, make_review


def _customer(id="cust1"): return make_user(id=id, role=UserRole.CUSTOMER)
def _admin():               return make_user(id="admin1", role=UserRole.ADMIN)


class TestSubmitReview:
    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        db.__getitem__ = MagicMock(return_value=AsyncMock())
        return db

    async def test_submit_review_success(self, mock_db):
        review = make_review()
        with patch("app.services.review_service.ReviewRepository") as R, \
             patch("app.services.review_service.notify_all_admins"), \
             patch("app.services.review_service.inc_metric"):
            R.return_value.create = AsyncMock(return_value=review)
            R.return_value.collection = MagicMock(database=mock_db)
            result = await ReviewService(mock_db).submit_review(
                CreateReviewRequest(rating=5, category="overall", message="Great service"),
                _customer()
            )
        assert result.rating == 5
        assert result.customer_id == "cust1" or result.category == "overall"

    async def test_review_stores_customer_name(self, mock_db):
        review = make_review(customer_id="cust1")
        with patch("app.services.review_service.ReviewRepository") as R, \
             patch("app.services.review_service.notify_all_admins"), \
             patch("app.services.review_service.inc_metric"):
            R.return_value.create = AsyncMock(return_value=review)
            R.return_value.collection = MagicMock(database=mock_db)
            await ReviewService(mock_db).submit_review(
                CreateReviewRequest(rating=4, category="service", message="Great"),
                _customer()
            )
            doc = R.return_value.create.call_args[0][0]
            assert doc["customer_id"] == "cust1"
            assert "customer_name" in doc


class TestGetMyReviews:
    @pytest.fixture
    def mock_db(self): return AsyncMock()

    async def test_customer_sees_only_own_reviews(self, mock_db):
        reviews = [make_review(customer_id="cust1"), make_review(id="rev2", customer_id="cust1")]
        with patch("app.services.review_service.ReviewRepository") as R, \
             patch("app.services.review_service.inc_metric"):
            R.return_value.find_by_customer = AsyncMock(return_value=reviews)
            result = await ReviewService(mock_db).get_my_reviews(_customer())
        assert len(result) == 2
        R.return_value.find_by_customer.assert_called_once_with("cust1")

    async def test_get_my_reviews_empty(self, mock_db):
        with patch("app.services.review_service.ReviewRepository") as R, \
             patch("app.services.review_service.inc_metric"):
            R.return_value.find_by_customer = AsyncMock(return_value=[])
            result = await ReviewService(mock_db).get_my_reviews(_customer())
        assert result == []


class TestGetAllReviews:
    @pytest.fixture
    def mock_db(self): return AsyncMock()

    async def test_admin_sees_all_reviews(self, mock_db):
        reviews = [make_review(customer_id="c1"), make_review(id="r2", customer_id="c2")]
        with patch("app.services.review_service.ReviewRepository") as R, \
             patch("app.services.review_service.inc_metric"):
            R.return_value.find_all = AsyncMock(return_value=reviews)
            result = await ReviewService(mock_db).get_all_reviews(_admin())
        assert len(result) == 2

    async def test_customer_cannot_get_all_reviews(self, mock_db):
        with patch("app.services.review_service.ReviewRepository"):
            with pytest.raises(ForbiddenException):
                await ReviewService(mock_db).get_all_reviews(_customer())