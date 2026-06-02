from pydantic import BaseModel
from typing import List
from datetime import datetime


class MetricsHourlyResponse(BaseModel):
    hour: datetime
    new_users: int
    logins_success: int
    logins_failed: int
    requests_submitted: int
    projects_created: int
    reviews_submitted: int
    books_added: int
    errors_count: int


class MetricsSummaryResponse(BaseModel):
    # Today
    today_new_users: int
    today_logins: int
    today_failed_logins: int
    today_requests: int
    today_reviews: int
    today_errors: int
    # This week
    week_new_users: int
    week_logins: int
    week_requests: int
    week_reviews: int
    week_errors: int
    # All time totals from MongoDB counts
    total_users: int
    total_books: int
    total_requests: int
    total_projects: int
    total_reviews: int


class MetricsTrendResponse(BaseModel):
    data: List[MetricsHourlyResponse]