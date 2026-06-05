import pytest
from unittest.mock import AsyncMock, patch
from app.services.audit_log_service import audit


class TestAuditHelper:
    @pytest.fixture
    def mock_db(self): return AsyncMock()

    async def test_audit_creates_log(self, mock_db):
        with patch("app.services.audit_log_service.AuditLogRepository") as R:
            R.return_value.create = AsyncMock()
            await audit(
                db=mock_db, actor_id="user1", actor_name="Test",
                actor_role="admin", action="book_created",
                description="Book added",
            )
            R.return_value.create.assert_called_once()
            doc = R.return_value.create.call_args[0][0]
            assert doc["action"] == "book_created"
            assert doc["actor_id"] == "user1"

    async def test_audit_is_silent_on_failure(self, mock_db):
        with patch("app.services.audit_log_service.AuditLogRepository") as R:
            R.return_value.create = AsyncMock(side_effect=Exception("DB error"))
            # Should not raise
            await audit(
                db=mock_db, actor_id="u1", actor_name="T",
                actor_role="admin", action="test", description="test"
            )

    async def test_audit_stores_metadata(self, mock_db):
        with patch("app.services.audit_log_service.AuditLogRepository") as R:
            R.return_value.create = AsyncMock()
            await audit(
                db=mock_db, actor_id="u1", actor_name="T",
                actor_role="admin", action="book_updated",
                description="Updated", entity_type="book",
                entity_id="book1",
                metadata={"updated_fields": ["price", "stock"]},
            )
            doc = R.return_value.create.call_args[0][0]
            assert doc["entity_type"] == "book"
            assert doc["entity_id"] == "book1"
            assert doc["metadata"]["updated_fields"] == ["price", "stock"]

    async def test_audit_with_ip_address(self, mock_db):
        with patch("app.services.audit_log_service.AuditLogRepository") as R:
            R.return_value.create = AsyncMock()
            await audit(
                db=mock_db, actor_id="u1", actor_name="T",
                actor_role="customer", action="user_registered",
                description="Registered", ip_address="192.168.1.1",
            )
            doc = R.return_value.create.call_args[0][0]
            assert doc["ip_address"] == "192.168.1.1"