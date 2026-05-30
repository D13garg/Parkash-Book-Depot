from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from app.models.audit_log import AuditLogModel

COLLECTION = "audit_logs"


class AuditLogRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION]

    def _doc_to_model(self, doc: dict) -> AuditLogModel:
        doc["_id"] = str(doc["_id"])
        return AuditLogModel(**doc)

    async def create(self, data: dict) -> AuditLogModel:
        result = await self.collection.insert_one(data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        return self._doc_to_model(doc)

    async def find_all(
        self,
        action: Optional[str] = None,
        actor_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[AuditLogModel], int]:
        query = {}
        if action:
            query["action"] = action
        if actor_id:
            query["actor_id"] = actor_id
        if entity_type:
            query["entity_type"] = entity_type
        if from_date:
            query["created_at"] = {"$gte": from_date}
        total = await self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._doc_to_model(d) for d in docs], total

    async def find_by_entity(self, entity_type: str, entity_id: str) -> list[AuditLogModel]:
        cursor = self.collection.find(
            {"entity_type": entity_type, "entity_id": entity_id}
        ).sort("created_at", -1)
        docs = await cursor.to_list(length=None)
        return [self._doc_to_model(d) for d in docs]