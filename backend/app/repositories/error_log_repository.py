from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from app.models.error_log import ErrorLogModel

COLLECTION = "error_logs"


class ErrorLogRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION]

    def _doc_to_model(self, doc: dict) -> ErrorLogModel:
        doc["_id"] = str(doc["_id"])
        return ErrorLogModel(**doc)

    async def create(self, data: dict) -> None:
        await self.collection.insert_one(data)

    async def find_all(
        self,
        level: Optional[str] = None,
        endpoint: Optional[str] = None,
        from_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[ErrorLogModel], int]:
        query = {}
        if level:
            query["level"] = level
        if endpoint:
            query["endpoint"] = {"$regex": endpoint, "$options": "i"}
        if from_date:
            query["created_at"] = {"$gte": from_date}
        total = await self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._doc_to_model(d) for d in docs], total