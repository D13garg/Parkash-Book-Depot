from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional
from datetime import datetime, timezone

from app.models.user import UserModel


COLLECTION = "users"


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION]

    async def find_by_email(self, email: str) -> Optional[UserModel]:
        doc = await self.collection.find_one({"email": email})
        if doc:
            doc["_id"] = str(doc["_id"])
            return UserModel(**doc)
        return None

    async def find_by_id(self, user_id: str) -> Optional[UserModel]:
        if not ObjectId.is_valid(user_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
            return UserModel(**doc)
        return None

    async def create(self, user_data: dict) -> UserModel:
        result = await self.collection.insert_one(user_data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        doc["_id"] = str(doc["_id"])
        return UserModel(**doc)

    async def email_exists(self, email: str) -> bool:
        doc = await self.collection.find_one({"email": email}, {"_id": 1})
        return doc is not None

    async def update(self, user_id: str, update_data: dict) -> Optional[UserModel]:
        update_data["updated_at"] = datetime.now(timezone.utc)
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return await self.find_by_id(user_id)
