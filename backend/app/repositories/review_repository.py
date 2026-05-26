from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models.review import ReviewModel

COLLECTION = "reviews"


class ReviewRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION]

    def _doc_to_model(self, doc: dict) -> ReviewModel:
        doc["_id"] = str(doc["_id"])
        return ReviewModel(**doc)

    async def create(self, data: dict) -> ReviewModel:
        result = await self.collection.insert_one(data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        return self._doc_to_model(doc)

    async def find_by_customer(self, customer_id: str) -> List[ReviewModel]:
        cursor = self.collection.find({"customer_id": customer_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=None)
        return [self._doc_to_model(d) for d in docs]

    async def find_all(self) -> List[ReviewModel]:
        cursor = self.collection.find().sort("created_at", -1)
        docs = await cursor.to_list(length=None)
        return [self._doc_to_model(d) for d in docs]

    async def find_by_id(self, review_id: str) -> Optional[ReviewModel]:
        if not ObjectId.is_valid(review_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(review_id)})
        return self._doc_to_model(doc) if doc else None