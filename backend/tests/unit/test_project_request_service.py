import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.project_request_service import ProjectRequestService
from app.schemas.project_request import CreateProjectRequestRequest, UpdateRequestStatusRequest
from app.core.enums import ProjectRequestStatus, UserRole
from app.core.exceptions import ForbiddenException, InvalidStateTransitionException, NotFoundException
from tests.conftest import make_user, make_project_request


def _customer():
    return make_user(id="cust1", role=UserRole.CUSTOMER)

def _admin():
    return make_user(id="admin1", role=UserRole.ADMIN)

def _associate():
    return make_user(id="assoc1", role=UserRole.ASSOCIATE)


class TestSubmitRequest:
    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        db.__getitem__ = MagicMock(return_value=AsyncMock())
        return db

    async def test_customer_can_submit(self, mock_db):
        req = make_project_request()
        with patch("app.services.project_request_service.ProjectRequestRepository") as R, \
             patch("app.services.project_request_service.notify_all_admins"), \
             patch("app.services.project_request_service.audit"), \
             patch("app.services.project_request_service.inc_metric"):
            R.return_value.create = AsyncMock(return_value=req)
            R.return_value.collection = MagicMock(database=mock_db)
            result = await ProjectRequestService(mock_db).submit_request(
                CreateProjectRequestRequest(
                    title="Test Request", description="A detailed description",
                    category="bulk_order", request_type="project"
                ),
                _customer()
            )
        assert result.customer_id == "cust1" or result.title == "Test Request"

    async def test_associate_cannot_submit(self, mock_db):
        with patch("app.services.project_request_service.ProjectRequestRepository"):
            with pytest.raises(ForbiddenException):
                await ProjectRequestService(mock_db).submit_request(
                    CreateProjectRequestRequest(
                        title="Test", description="A detailed description",
                        category="bulk_order", request_type="project"
                    ),
                    _associate()
                )

    async def test_admin_cannot_submit(self, mock_db):
        with patch("app.services.project_request_service.ProjectRequestRepository"):
            with pytest.raises(ForbiddenException):
                await ProjectRequestService(mock_db).submit_request(
                    CreateProjectRequestRequest(
                        title="Test", description="A detailed description",
                        category="bulk_order", request_type="project"
                    ),
                    _admin()
                )


class TestUpdateStatus:
    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        db.__getitem__ = MagicMock(return_value=AsyncMock())
        return db

    async def test_valid_transition_succeeds(self, mock_db):
        req = make_project_request(status=ProjectRequestStatus.SUBMITTED)
        updated = make_project_request(status=ProjectRequestStatus.UNDER_REVIEW)
        with patch("app.services.project_request_service.ProjectRequestRepository") as R, \
             patch("app.services.project_request_service.audit"), \
             patch("app.services.project_request_service.inc_metric"):
            R.return_value.find_by_id = AsyncMock(return_value=req)
            R.return_value.update_status = AsyncMock(return_value=updated)
            R.return_value.collection = MagicMock(database=mock_db)
            result = await ProjectRequestService(mock_db).update_status(
                "req123",
                UpdateRequestStatusRequest(status=ProjectRequestStatus.UNDER_REVIEW),
                _admin()
            )
        assert result.status == ProjectRequestStatus.UNDER_REVIEW

    async def test_invalid_transition_raises(self, mock_db):
        req = make_project_request(status=ProjectRequestStatus.SUBMITTED)
        with patch("app.services.project_request_service.ProjectRequestRepository") as R, \
             patch("app.services.project_request_service.audit"), \
             patch("app.services.project_request_service.inc_metric"):
            R.return_value.find_by_id = AsyncMock(return_value=req)
            R.return_value.collection = MagicMock(database=mock_db)
            with pytest.raises(InvalidStateTransitionException):
                await ProjectRequestService(mock_db).update_status(
                    "req123",
                    UpdateRequestStatusRequest(status=ProjectRequestStatus.ACCEPTED),
                    _admin()
                )

    async def test_reject_without_reason_raises(self, mock_db):
        req = make_project_request(status=ProjectRequestStatus.UNDER_REVIEW)
        with patch("app.services.project_request_service.ProjectRequestRepository") as R, \
             patch("app.services.project_request_service.audit"), \
             patch("app.services.project_request_service.inc_metric"):
            R.return_value.find_by_id = AsyncMock(return_value=req)
            R.return_value.collection = MagicMock(database=mock_db)
            with pytest.raises(Exception):
                await ProjectRequestService(mock_db).update_status(
                    "req123",
                    UpdateRequestStatusRequest(
                        status=ProjectRequestStatus.REJECTED,
                        rejection_reason=None
                    ),
                    _admin()
                )

    async def test_request_not_found_raises(self, mock_db):
        with patch("app.services.project_request_service.ProjectRequestRepository") as R, \
             patch("app.services.project_request_service.audit"), \
             patch("app.services.project_request_service.inc_metric"):
            R.return_value.find_by_id = AsyncMock(return_value=None)
            R.return_value.collection = MagicMock(database=mock_db)
            with pytest.raises(NotFoundException):
                await ProjectRequestService(mock_db).update_status(
                    "bad_id",
                    UpdateRequestStatusRequest(status=ProjectRequestStatus.UNDER_REVIEW),
                    _admin()
                )