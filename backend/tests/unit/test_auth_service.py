import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.auth_service import AuthService
from app.schemas.user import RegisterRequest, LoginRequest
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import hash_password
from app.core.enums import UserRole
from tests.conftest import make_user


class TestRegister:
    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        db.__getitem__ = MagicMock(return_value=AsyncMock())
        return db

    async def test_register_success(self, mock_db):
        user = make_user(email="john@gmail.com")
        with patch("app.services.auth_service.UserRepository") as R, \
             patch("app.services.auth_service.audit"), \
             patch("app.services.auth_service.inc_metric"):
            r = R.return_value
            r.email_exists = AsyncMock(return_value=False)
            r.create = AsyncMock(return_value=user)
            result = await AuthService(mock_db).register(
                RegisterRequest(name="Test User", email="john@gmail.com", password="Password1!")
            )
        assert result.user.email == "john@gmail.com"
        assert result.access_token is not None
        assert result.refresh_token is not None

    async def test_register_duplicate_email_raises(self, mock_db):
        with patch("app.services.auth_service.UserRepository") as R:
            R.return_value.email_exists = AsyncMock(return_value=True)
            with pytest.raises(ConflictException):
                await AuthService(mock_db).register(
                    RegisterRequest(name="Test", email="john@gmail.com", password="Password1!")
                )

    async def test_register_creates_customer_role(self, mock_db):
        user = make_user(role=UserRole.CUSTOMER, email="john@gmail.com")
        with patch("app.services.auth_service.UserRepository") as R, \
             patch("app.services.auth_service.audit"), \
             patch("app.services.auth_service.inc_metric"):
            r = R.return_value
            r.email_exists = AsyncMock(return_value=False)
            r.create = AsyncMock(return_value=user)
            result = await AuthService(mock_db).register(
                RegisterRequest(name="Test User", email="john@gmail.com", password="Password1!")
            )
            call_args = r.create.call_args[0][0]
            assert call_args["role"] == UserRole.CUSTOMER.value


class TestLogin:
    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        db.__getitem__ = MagicMock(return_value=AsyncMock())
        return db

    async def test_login_success(self, mock_db):
        user = make_user(email="john@gmail.com")
        user.hashed_password = hash_password("Password1!")
        with patch("app.services.auth_service.UserRepository") as R, \
             patch("app.services.auth_service.audit"), \
             patch("app.services.auth_service.log_error"), \
             patch("app.services.auth_service.inc_metric"):
            R.return_value.find_by_email = AsyncMock(return_value=user)
            result = await AuthService(mock_db).login(
                LoginRequest(email="john@gmail.com", password="Password1!")
            )
        assert result.access_token is not None
        assert result.user.email == "john@gmail.com"

    async def test_login_wrong_password_raises(self, mock_db):
        user = make_user(email="john@gmail.com")
        user.hashed_password = hash_password("Password1!")
        with patch("app.services.auth_service.UserRepository") as R, \
             patch("app.services.auth_service.audit"), \
             patch("app.services.auth_service.log_error"), \
             patch("app.services.auth_service.inc_metric"):
            R.return_value.find_by_email = AsyncMock(return_value=user)
            with pytest.raises(UnauthorizedException):
                await AuthService(mock_db).login(
                    LoginRequest(email="john@gmail.com", password="WrongPass1!")
                )

    async def test_login_user_not_found_raises(self, mock_db):
        with patch("app.services.auth_service.UserRepository") as R, \
             patch("app.services.auth_service.audit"), \
             patch("app.services.auth_service.log_error"), \
             patch("app.services.auth_service.inc_metric"):
            R.return_value.find_by_email = AsyncMock(return_value=None)
            with pytest.raises(UnauthorizedException):
                await AuthService(mock_db).login(
                    LoginRequest(email="nobody@gmail.com", password="Password1!")
                )

    async def test_login_inactive_user_raises(self, mock_db):
        user = make_user(is_active=False, email="john@gmail.com")
        user.hashed_password = hash_password("Password1!")
        with patch("app.services.auth_service.UserRepository") as R, \
             patch("app.services.auth_service.audit"), \
             patch("app.services.auth_service.log_error"), \
             patch("app.services.auth_service.inc_metric"):
            R.return_value.find_by_email = AsyncMock(return_value=user)
            with pytest.raises(UnauthorizedException):
                await AuthService(mock_db).login(
                    LoginRequest(email="john@gmail.com", password="Password1!")
                )