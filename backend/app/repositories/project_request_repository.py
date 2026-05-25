from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional
from datetime import datetime, timezone

from app.models.project_request import ProjectRequestModel

COLLECTION = "project_requests"


class ProjectRequestRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION]

    def _doc_to_model(self, doc: dict) -> ProjectRequestModel:
        doc["_id"] = str(doc["_id"])
        return ProjectRequestModel(**doc)

    async def create(self, data: dict) -> ProjectRequestModel:
        result = await self.collection.insert_one(data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        return self._doc_to_model(doc)

    async def find_by_id(self, request_id: str) -> Optional[ProjectRequestModel]:
        if not ObjectId.is_valid(request_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(request_id)})
        return self._doc_to_model(doc) if doc else None

    async def find_by_customer(
        self,
        customer_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[ProjectRequestModel], int]:
        query = {"customer_id": customer_id}
        total = await self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._doc_to_model(d) for d in docs], total

    async def find_all(
        self,
        *,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[ProjectRequestModel], int]:
        query = {}
        if status:
            query["status"] = status
        total = await self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._doc_to_model(d) for d in docs], total

    async def update_status(self, request_id: str, update_data: dict) -> Optional[ProjectRequestModel]:
        update_data["updated_at"] = datetime.now(timezone.utc)
        await self.collection.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": update_data}
        )
        return await self.find_by_id(request_id)
