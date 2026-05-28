from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models.gallery import GalleryItemModel

COLLECTION = "gallery"


class GalleryRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION]

    def _doc_to_model(self, doc: dict) -> GalleryItemModel:
        doc["_id"] = str(doc["_id"])
        return GalleryItemModel(**doc)

    async def create(self, data: dict) -> GalleryItemModel:
        result = await self.collection.insert_one(data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        return self._doc_to_model(doc)

    async def find_all(self) -> List[GalleryItemModel]:
        cursor = self.collection.find().sort("created_at", -1)
        docs = await cursor.to_list(length=None)
        return [self._doc_to_model(d) for d in docs]

    async def find_by_id(self, item_id: str) -> Optional[GalleryItemModel]:
        if not ObjectId.is_valid(item_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(item_id)})
        return self._doc_to_model(doc) if doc else None

    async def update_caption(self, item_id: str, caption: str) -> Optional[GalleryItemModel]:
        await self.collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": {"caption": caption}}
        )
        return await self.find_by_id(item_id)

    async def delete(self, item_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count == 1