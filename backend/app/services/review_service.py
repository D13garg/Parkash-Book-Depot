from typing import List

from app.repositories.review_repository import (
    ReviewRepository,
)

from app.schemas.review import (
    ReviewCreate,
)

from app.models.review import ReviewModel


class ReviewService:
    def __init__(
        self,
        repository: ReviewRepository,
    ):
        self.repository = repository

    async def create_review(
        self,
        payload: ReviewCreate,
    ) -> ReviewModel:
        return await self.repository.create_review(
            payload.model_dump()
        )

    async def get_reviews(
        self,
    ) -> List[ReviewModel]:
        return await self.repository.get_reviews()

    async def get_reviews_by_reviewer(
        self,
        reviewer_email: str,
    ) -> List[ReviewModel]:
        return await self.repository.find_by_reviewer_email(reviewer_email)