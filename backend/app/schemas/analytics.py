from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ExecutiveSummary(BaseModel):
    total_requests: int
    total_projects: int
    completed_projects: int
    completion_rate_percent: float
    total_reviews: int
    low_stock_count: int
    error_count_24h: int


class AssociatePerformance(BaseModel):
    associate_id: str
    associate_name: str
    associate_email: str
    assigned_projects: int
    completed_projects: int
    open_projects: int
    avg_completion_days: Optional[float] = None


class ReviewMetrics(BaseModel):
    average_rating: float
    total_reviews: int
    reviews_this_month: int


class LowStockBook(BaseModel):
    id: str
    title: str
    stock: int
    low_stock_threshold: int


class StaleRequest(BaseModel):
    id: str
    title: str
    category: str
    status: str
    days_old: int
    customer_id: str


class InactiveProject(BaseModel):
    id: str
    title: str
    status: str
    assigned_to: Optional[str] = None
    days_since_update: int


class AnalyticsResponse(BaseModel):
    summary: ExecutiveSummary
    request_conversion_rate: float
    associate_performance: List[AssociatePerformance]
    review_metrics: ReviewMetrics
    low_stock_books: List[LowStockBook]
    stale_requests: List[StaleRequest]
    inactive_projects: List[InactiveProject]