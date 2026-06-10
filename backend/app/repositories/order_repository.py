from typing import List, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timezone
from app.models.order import OrderModel

COLLECTION = "orders"


class OrderRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION]

    def _doc_to_model(self, doc: dict) -> OrderModel:
        doc["_id"] = str(doc["_id"])
        return OrderModel(**doc)

    async def create(self, data: dict) -> OrderModel:
        result = await self.collection.insert_one(data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        return self._doc_to_model(doc)

    async def find_by_id(self, order_id: str) -> Optional[OrderModel]:
        if not ObjectId.is_valid(order_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(order_id)})
        return self._doc_to_model(doc) if doc else None

    async def find_by_customer(self, customer_id: str, skip=0, limit=20) -> Tuple[List[OrderModel], int]:
        query = {"customer_id": customer_id}
        total = await self.collection.count_documents(query)
        docs = await self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        return [self._doc_to_model(d) for d in docs], total

    async def find_all(self, status: Optional[str]=None, skip=0, limit=20) -> Tuple[List[OrderModel], int]:
        query = {"status": status} if status else {}
        total = await self.collection.count_documents(query)
        docs = await self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        return [self._doc_to_model(d) for d in docs], total

    async def update_status(self, order_id: str, status: str) -> Optional[OrderModel]:
        await self.collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"status": status, "updated_at": datetime.now(timezone.utc)}}
        )
        return await self.find_by_id(order_id)