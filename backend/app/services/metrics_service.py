from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.metrics_repository import MetricsRepository
from app.schemas.metrics import MetricsSummaryResponse, MetricsTrendResponse, MetricsHourlyResponse


async def increment(db: AsyncIOMotorDatabase, field: str, amount: int = 1) -> None:
    """Silent metrics counter — never raises."""
    try:
        repo = MetricsRepository(db)
        await repo.increment(field, amount)
    except Exception:
        pass


def _sum_field(records, field: str) -> int:
    return sum(getattr(r, field, 0) for r in records)


class MetricsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = MetricsRepository(db)
        self.db = db

    async def get_summary(self) -> MetricsSummaryResponse:
        today = await self.repo.find_today()
        week = await self.repo.find_week()

        # All-time counts from MongoDB collections
        total_users    = await self.db["users"].count_documents({})
        total_books    = await self.db["books"].count_documents({"is_active": True})
        total_requests = await self.db["project_requests"].count_documents({})
        total_projects = await self.db["projects"].count_documents({})
        total_reviews  = await self.db["reviews"].count_documents({})

        return MetricsSummaryResponse(
            today_new_users=_sum_field(today, "new_users"),
            today_logins=_sum_field(today, "logins_success"),
            today_failed_logins=_sum_field(today, "logins_failed"),
            today_requests=_sum_field(today, "requests_submitted"),
            today_reviews=_sum_field(today, "reviews_submitted"),
            today_errors=_sum_field(today, "errors_count"),
            week_new_users=_sum_field(week, "new_users"),
            week_logins=_sum_field(week, "logins_success"),
            week_requests=_sum_field(week, "requests_submitted"),
            week_reviews=_sum_field(week, "reviews_submitted"),
            week_errors=_sum_field(week, "errors_count"),
            total_users=total_users,
            total_books=total_books,
            total_requests=total_requests,
            total_projects=total_projects,
            total_reviews=total_reviews,
        )

    async def get_trend(self) -> MetricsTrendResponse:
        records = await self.repo.find_last_30_days()
        return MetricsTrendResponse(
            data=[
                MetricsHourlyResponse(
                    hour=r.hour,
                    new_users=r.new_users,
                    logins_success=r.logins_success,
                    logins_failed=r.logins_failed,
                    requests_submitted=r.requests_submitted,
                    projects_created=r.projects_created,
                    reviews_submitted=r.reviews_submitted,
                    books_added=r.books_added,
                    errors_count=r.errors_count,
                )
                for r in records
            ]
        )