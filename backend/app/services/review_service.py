from typing import List
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.review_repository import ReviewRepository
from app.schemas.review import CreateReviewRequest, UpdateReviewRequest, ReviewResponse
from app.models.user import UserModel
from app.core.exceptions import ForbiddenException, NotFoundException
from app.permissions.role_permissions import is_admin
from app.services.notification_service import notify_all_admins
from app.services.metrics_service import increment as inc_metric


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
        now = datetime.now(timezone.utc)
        doc = {
            "customer_id": current_user.id,
            "customer_name": current_user.name,
            "rating": data.rating,
            "category": data.category,
            "message": data.message,
            "created_at": now,
            "updated_at": now,
        }
        review = await self.repo.create(doc)

        # Notify all admins
        await notify_all_admins(
            db=self.repo.collection.database,
            type="review_submitted",
            message=f"New {data.rating}★ review from {current_user.name}: \"{data.category}\"",
            link="/admin/reviews",
        )

        await inc_metric(self.repo.collection.database, "reviews_submitted")
        return _to_response(review)

    async def get_my_reviews(self, current_user: UserModel) -> List[ReviewResponse]:
        reviews = await self.repo.find_by_customer(current_user.id)
        return [_to_response(r) for r in reviews]

    async def get_all_reviews(self, current_user: UserModel) -> List[ReviewResponse]:
        if not is_admin(current_user):
            raise ForbiddenException("Admin access required.")
        reviews = await self.repo.find_all()
        return [_to_response(r) for r in reviews]

    async def update_review(
        self, review_id: str, data: UpdateReviewRequest, current_user: UserModel
    ) -> ReviewResponse:
        review = await self.repo.find_by_id(review_id)
        if not review:
            raise NotFoundException("Review")
        if review.customer_id != current_user.id:
            raise ForbiddenException("You can only edit your own reviews.")

        update = {k: v for k, v in {
            "rating": data.rating,
            "category": data.category,
            "message": data.message,
            "updated_at": datetime.now(timezone.utc),
        }.items() if v is not None}

        updated = await self.repo.update(review_id, update)
        return _to_response(updated)

    async def delete_review(self, review_id: str, current_user: UserModel) -> None:
        review = await self.repo.find_by_id(review_id)
        if not review:
            raise NotFoundException("Review")
        # Customer can delete their own; admin can delete any
        if review.customer_id != current_user.id and not is_admin(current_user):
            raise ForbiddenException("You can only delete your own reviews.")
        await self.repo.delete(review_id)