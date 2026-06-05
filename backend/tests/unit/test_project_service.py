import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.project_service import ProjectService
from app.schemas.project import AssignProjectRequest, UpdateProjectStatusRequest
from app.core.enums import ProjectStatus, ProjectRequestStatus, UserRole
from app.core.exceptions import NotFoundException, BadRequestException, InvalidStateTransitionException, ForbiddenException
from tests.conftest import make_user, make_project, make_project_request


def _admin():    return make_user(id="admin1", role=UserRole.ADMIN)
def _associate(): return make_user(id="assoc1", role=UserRole.ASSOCIATE)
def _customer():  return make_user(id="cust1",  role=UserRole.CUSTOMER)


def _mock_service(mock_db):
    svc = ProjectService(mock_db)
    svc.project_repo = AsyncMock()
    svc.update_repo  = AsyncMock()
    svc.request_repo = AsyncMock()
    svc.project_repo.collection = MagicMock(database=mock_db)
    return svc


class TestConvertRequest:
    @pytest.fixture
    def mock_db(self): return AsyncMock()

    async def test_convert_accepted_request(self, mock_db):
        req  = make_project_request(status=ProjectRequestStatus.ACCEPTED)
        proj = make_project()
        with patch("app.services.project_service.audit"), \
             patch("app.services.project_service.inc_metric"):
            svc = _mock_service(mock_db)
            svc.request_repo.find_by_id  = AsyncMock(return_value=req)
            svc.request_repo.update_status = AsyncMock()
            svc.project_repo.create      = AsyncMock(return_value=proj)
            svc.update_repo.create       = AsyncMock()
            result = await svc.convert_request_to_project("req123", _admin())
        assert result.id == "proj123"

    async def test_convert_non_accepted_raises(self, mock_db):
        req = make_project_request(status=ProjectRequestStatus.SUBMITTED)
        svc = _mock_service(mock_db)
        svc.request_repo.find_by_id = AsyncMock(return_value=req)
        with pytest.raises(BadRequestException):
            await svc.convert_request_to_project("req123", _admin())

    async def test_convert_not_found_raises(self, mock_db):
        svc = _mock_service(mock_db)
        svc.request_repo.find_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await svc.convert_request_to_project("bad", _admin())


class TestAssignAssociate:
    @pytest.fixture
    def mock_db(self): return AsyncMock()

    async def test_assign_pending_project(self, mock_db):
        proj    = make_project(status=ProjectStatus.PENDING)
        updated = make_project(status=ProjectStatus.ASSIGNED, assigned_to="assoc1")
        with patch("app.services.project_service.notify"), \
             patch("app.services.project_service.audit"), \
             patch("app.services.project_service.inc_metric"):
            svc = _mock_service(mock_db)
            svc.project_repo.find_by_id       = AsyncMock(return_value=proj)
            svc.project_repo.assign_associate = AsyncMock(return_value=updated)
            svc.update_repo.create            = AsyncMock()
            result = await svc.assign_associate("proj123", AssignProjectRequest(associate_id="assoc1"), _admin())
        assert result.assigned_to == "assoc1"

    async def test_assign_completed_project_raises(self, mock_db):
        proj = make_project(status=ProjectStatus.COMPLETED)
        svc  = _mock_service(mock_db)
        svc.project_repo.find_by_id = AsyncMock(return_value=proj)
        with pytest.raises(BadRequestException):
            await svc.assign_associate("proj123", AssignProjectRequest(associate_id="assoc1"), _admin())


class TestGetProject:
    @pytest.fixture
    def mock_db(self): return AsyncMock()

    async def test_admin_can_view_any_project(self, mock_db):
        proj = make_project(assigned_to="other")
        svc  = _mock_service(mock_db)
        svc.project_repo.find_by_id = AsyncMock(return_value=proj)
        result = await svc.get_project("proj123", _admin())
        assert result.id == "proj123"

    async def test_assigned_associate_can_view(self, mock_db):
        proj = make_project(assigned_to="assoc1")
        svc  = _mock_service(mock_db)
        svc.project_repo.find_by_id = AsyncMock(return_value=proj)
        result = await svc.get_project("proj123", _associate())
        assert result.id == "proj123"

    async def test_unassigned_associate_cannot_view(self, mock_db):
        proj = make_project(assigned_to="other_assoc")
        svc  = _mock_service(mock_db)
        svc.project_repo.find_by_id = AsyncMock(return_value=proj)
        with pytest.raises(ForbiddenException):
            await svc.get_project("proj123", _associate())

    async def test_customer_cannot_view_project(self, mock_db):
        proj = make_project()
        svc  = _mock_service(mock_db)
        svc.project_repo.find_by_id = AsyncMock(return_value=proj)
        with pytest.raises(ForbiddenException):
            await svc.get_project("proj123", _customer())


class TestUpdateStatus:
    @pytest.fixture
    def mock_db(self): return AsyncMock()

    async def test_valid_transition_succeeds(self, mock_db):
        proj    = make_project(status=ProjectStatus.ASSIGNED)
        updated = make_project(status=ProjectStatus.IN_PROGRESS)
        with patch("app.services.project_service.audit"), \
             patch("app.services.project_service.inc_metric"):
            svc = _mock_service(mock_db)
            svc.project_repo.find_by_id = AsyncMock(return_value=proj)
            svc.project_repo.update     = AsyncMock(return_value=updated)
            svc.update_repo.create      = AsyncMock()
            result = await svc.update_status(
                "proj123",
                UpdateProjectStatusRequest(status=ProjectStatus.IN_PROGRESS),
                _admin()
            )
        assert result.status == ProjectStatus.IN_PROGRESS

    async def test_invalid_transition_raises(self, mock_db):
        proj = make_project(status=ProjectStatus.COMPLETED)
        with patch("app.services.project_service.audit"), \
             patch("app.services.project_service.inc_metric"):
            svc = _mock_service(mock_db)
            svc.project_repo.find_by_id = AsyncMock(return_value=proj)
            with pytest.raises(InvalidStateTransitionException):
                await svc.update_status(
                    "proj123",
                    UpdateProjectStatusRequest(status=ProjectStatus.IN_PROGRESS),
                    _admin()
                )