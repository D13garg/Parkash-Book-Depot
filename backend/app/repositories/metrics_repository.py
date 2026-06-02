from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import List
from app.models.metrics import MetricsHourlyModel

COLLECTION = "metrics_hourly"


class MetricsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION]

    def _doc_to_model(self, doc: dict) -> MetricsHourlyModel:
        doc["_id"] = str(doc["_id"])
        return MetricsHourlyModel(**doc)

    def _current_hour(self) -> datetime:
        now = datetime.now(timezone.utc)
        return now.replace(minute=0, second=0, microsecond=0)

    async def increment(self, field: str, amount: int = 1) -> None:
        hour = self._current_hour()
        await self.collection.update_one(
            {"hour": hour},
            {"$inc": {field: amount}, "$setOnInsert": {"hour": hour}},
            upsert=True,
        )

    async def find_range(self, from_date: datetime, to_date: datetime) -> List[MetricsHourlyModel]:
        cursor = self.collection.find(
            {"hour": {"$gte": from_date, "$lte": to_date}}
        ).sort("hour", 1)
        docs = await cursor.to_list(length=None)
        return [self._doc_to_model(d) for d in docs]

    async def find_today(self) -> List[MetricsHourlyModel]:
        now = datetime.now(timezone.utc)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return await self.find_range(start, now)

    async def find_week(self) -> List[MetricsHourlyModel]:
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=7)
        return await self.find_range(start, now)

    async def find_last_30_days(self) -> List[MetricsHourlyModel]:
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=30)
        return await self.find_range(start, now)