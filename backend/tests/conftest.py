from app.core.enums import UserRole, ProjectRequestStatus, ProjectStatus
from datetime import datetime, timezone


def make_user(id="user123", name="Test User", email="test@example.com", role=UserRole.CUSTOMER, is_active=True):
    from app.models.user import UserModel
    return UserModel(_id=id, name=name, email=email, hashed_password="hashed", role=role, is_active=is_active, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))

def make_project_request(id="req123", customer_id="user123", status=ProjectRequestStatus.SUBMITTED):
    from app.models.project_request import ProjectRequestModel
    return ProjectRequestModel(_id=id, customer_id=customer_id, title="Test Request", description="A test project request description", category="bulk_order", status=status, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))

def make_project(id="proj123", request_id="req123", assigned_to=None, status=ProjectStatus.PENDING):
    from app.models.project import ProjectModel
    return ProjectModel(_id=id, request_id=request_id, created_by="admin123", assigned_to=assigned_to, title="Test Project", description="A test internal project", priority="medium", status=status, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))

def make_book(id="book123", stock=10, price=299.0):
    from app.models.book import BookModel
    return BookModel(_id=id, title="Test Book", authors=["Author One"], categories=["textbook"], price=price, stock=stock, low_stock_threshold=5, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
