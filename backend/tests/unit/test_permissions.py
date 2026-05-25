import pytest
from app.core.enums import UserRole
from app.core.exceptions import ForbiddenException
from app.permissions.role_permissions import require_admin, require_associate_or_admin, can_access_resource
from app.permissions.project_permissions import assert_can_view_project, assert_can_update_project
from app.permissions.project_request_permissions import assert_can_view_request, assert_can_submit_request
from tests.conftest import make_user, make_project, make_project_request

class TestRolePermissions:
    def test_admin_passes_require_admin(self):
        assert require_admin(make_user(role=UserRole.ADMIN)) is not None

    def test_customer_fails_require_admin(self):
        with pytest.raises(ForbiddenException):
            require_admin(make_user(role=UserRole.CUSTOMER))

    def test_associate_passes_require_associate_or_admin(self):
        assert require_associate_or_admin(make_user(role=UserRole.ASSOCIATE)) is not None

    def test_customer_fails_require_associate_or_admin(self):
        with pytest.raises(ForbiddenException):
            require_associate_or_admin(make_user(role=UserRole.CUSTOMER))

    def test_admin_can_access_any_resource(self):
        assert can_access_resource(make_user(id="admin1", role=UserRole.ADMIN), "someone_else") is True

    def test_user_can_access_own_resource(self):
        assert can_access_resource(make_user(id="user1"), "user1") is True

    def test_user_cannot_access_others_resource(self):
        assert can_access_resource(make_user(id="user1"), "user2") is False

class TestProjectPermissions:
    def test_admin_can_view_any_project(self):
        assert_can_view_project(make_user(role=UserRole.ADMIN), make_project(assigned_to="other"))

    def test_assigned_associate_can_view(self):
        assert_can_view_project(make_user(id="a1", role=UserRole.ASSOCIATE), make_project(assigned_to="a1"))

    def test_unassigned_associate_cannot_view(self):
        with pytest.raises(ForbiddenException):
            assert_can_view_project(make_user(id="a1", role=UserRole.ASSOCIATE), make_project(assigned_to="a2"))

    def test_customer_cannot_view_project(self):
        with pytest.raises(ForbiddenException):
            assert_can_view_project(make_user(role=UserRole.CUSTOMER), make_project())

class TestProjectRequestPermissions:
    def test_customer_can_view_own_request(self):
        assert_can_view_request(make_user(id="c1", role=UserRole.CUSTOMER), make_project_request(customer_id="c1"))

    def test_customer_cannot_view_others_request(self):
        with pytest.raises(ForbiddenException):
            assert_can_view_request(make_user(id="c1", role=UserRole.CUSTOMER), make_project_request(customer_id="c2"))

    def test_admin_can_view_any_request(self):
        assert_can_view_request(make_user(role=UserRole.ADMIN), make_project_request(customer_id="anyone"))

    def test_only_customers_can_submit(self):
        assert_can_submit_request(make_user(role=UserRole.CUSTOMER))

    def test_admin_cannot_submit(self):
        with pytest.raises(ForbiddenException):
            assert_can_submit_request(make_user(role=UserRole.ADMIN))
