from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.review import ReviewModel


class ReviewRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["reviews"]

    async def create_review(self, review_data: dict) -> ReviewModel:
        result = await self.collection.insert_one(review_data)

        created = await self.collection.find_one(
            {"_id": result.inserted_id}
        )

        created["_id"] = str(created["_id"])

        return ReviewModel(**created)

    async def get_reviews(self) -> List[ReviewModel]:
        reviews = []

        async for review in self.collection.find().sort(
            "created_at",
            -1
        ):
            review["_id"] = str(review["_id"])
            reviews.append(ReviewModel(**review))

        return reviews