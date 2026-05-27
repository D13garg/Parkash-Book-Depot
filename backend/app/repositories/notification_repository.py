from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timezone

from app.models.notification import NotificationModel

COLLECTION = "notifications"


class NotificationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION]

    def _doc_to_model(self, doc: dict) -> NotificationModel:
        doc["_id"] = str(doc["_id"])
        return NotificationModel(**doc)

    async def create(self, data: dict) -> NotificationModel:
        result = await self.collection.insert_one(data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        return self._doc_to_model(doc)

    async def find_by_user(self, user_id: str) -> List[NotificationModel]:
        cursor = self.collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(30)
        docs = await cursor.to_list(length=30)
        return [self._doc_to_model(d) for d in docs]

    async def unread_count(self, user_id: str) -> int:
        return await self.collection.count_documents(
            {"user_id": user_id, "is_read": False}
        )

    async def mark_read(self, notification_id: str, user_id: str) -> None:
        await self.collection.update_one(
            {"_id": ObjectId(notification_id), "user_id": user_id},
            {"$set": {"is_read": True}}
        )

    async def mark_all_read(self, user_id: str) -> None:
        await self.collection.update_many(
            {"user_id": user_id, "is_read": False},
            {"$set": {"is_read": True}}
        )

    async def find_admins(self, db: AsyncIOMotorDatabase) -> List[str]:
        """Returns list of admin user IDs — used to notify all admins."""
        cursor = db["users"].find({"role": "admin"}, {"_id": 1})
        docs = await cursor.to_list(length=None)
        return [str(d["_id"]) for d in docs]