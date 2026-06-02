from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


class MetricsHourlyModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    hour: datetime                  # rounded to hour — unique key
    new_users: int = 0
    logins_success: int = 0
    logins_failed: int = 0
    requests_submitted: int = 0
    projects_created: int = 0
    reviews_submitted: int = 0
    books_added: int = 0
    errors_count: int = 0

    class Config:
        populate_by_name = True