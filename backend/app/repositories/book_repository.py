from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional
from datetime import datetime, timezone

from app.models.book import BookModel

COLLECTION = "books"


class BookRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION]

    def _doc_to_model(self, doc: dict) -> BookModel:
        doc["_id"] = str(doc["_id"])
        return BookModel(**doc)

    async def find_by_id(self, book_id: str) -> Optional[BookModel]:
        if not ObjectId.is_valid(book_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(book_id), "is_active": True})
        return self._doc_to_model(doc) if doc else None

    async def find_many(
        self,
        *,
        category: Optional[str] = None,
        author: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock_only: bool = False,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[BookModel], int]:
        """
        Returns (list of books, total count) for the given filters.
        Both are needed to calculate pagination on the service layer.
        """
        query: dict = {"is_active": True}

        if category:
            query["categories"] = {"$in": [category]}
        if author:
            query["authors"] = {"$in": [author]}
        if min_price is not None or max_price is not None:
            query["price"] = {}
            if min_price is not None:
                query["price"]["$gte"] = min_price
            if max_price is not None:
                query["price"]["$lte"] = max_price
        if in_stock_only:
            query["stock"] = {"$gt": 0}
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"authors": {"$regex": search, "$options": "i"}},
            ]

        total = await self.collection.count_documents(query)
        cursor = self.collection.find(query).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        books = [self._doc_to_model(doc) for doc in docs]
        return books, total

    async def create(self, book_data: dict) -> BookModel:
        result = await self.collection.insert_one(book_data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        return self._doc_to_model(doc)

    async def update(self, book_id: str, update_data: dict) -> Optional[BookModel]:
        update_data["updated_at"] = datetime.now(timezone.utc)
        await self.collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$set": update_data}
        )
        return await self.find_by_id(book_id)

    async def soft_delete(self, book_id: str) -> bool:
        """Marks book as inactive instead of removing it from the DB."""
        result = await self.collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count == 1

    async def update_stock(self, book_id: str, new_stock: int) -> Optional[BookModel]:
        return await self.update(book_id, {"stock": new_stock})

    async def find_low_stock(self) -> list[BookModel]:
        """Returns all active books where stock < low_stock_threshold."""
        pipeline = [
            {"$match": {"is_active": True}},
            {"$match": {"$expr": {"$lt": ["$stock", "$low_stock_threshold"]}}}
        ]
        docs = await self.collection.aggregate(pipeline).to_list(length=None)
        return [self._doc_to_model(doc) for doc in docs]
