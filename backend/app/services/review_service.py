from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.review_repository import ReviewRepository
from app.schemas.review import CreateReviewRequest, ReviewResponse
from app.models.user import UserModel
from app.core.exceptions import ForbiddenException, NotFoundException
from app.permissions.role_permissions import is_admin


def _to_response(review) -> ReviewResponse:
    return ReviewResponse(
        id=review.id,
        customer_id=review.customer_id,
        customer_name=review.customer_name,
        rating=review.rating,
        category=review.category,
        message=review.message,
        created_at=review.created_at,
    )


class ReviewService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = ReviewRepository(db)

    async def submit_review(
        self, data: CreateReviewRequest, current_user: UserModel
    ) -> ReviewResponse:
        doc = {
            "customer_id": current_user.id,
            "customer_name": current_user.name,
            "rating": data.rating,
            "category": data.category,
            "message": data.message,
        }
        review = await self.repo.create(doc)
        return _to_response(review)

    async def get_my_reviews(self, current_user: UserModel) -> List[ReviewResponse]:
        reviews = await self.repo.find_by_customer(current_user.id)
        return [_to_response(r) for r in reviews]

    async def get_all_reviews(self, current_user: UserModel) -> List[ReviewResponse]:
        if not is_admin(current_user):
            raise ForbiddenException("Admin access required.")
        reviews = await self.repo.find_all()
        return [_to_response(r) for r in reviews]