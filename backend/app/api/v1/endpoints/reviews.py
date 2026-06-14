from typing import List
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user, get_current_admin
from app.services.review_service import ReviewService
from app.schemas.review import CreateReviewRequest, UpdateReviewRequest, ReviewResponse
from app.models.user import UserModel

router = APIRouter()


@router.post("", response_model=ReviewResponse, status_code=201)
async def submit_review(
    data: CreateReviewRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Customer submits a review. Auth required."""
    service = ReviewService(db)
    return await service.submit_review(data, current_user)


@router.get("/mine", response_model=List[ReviewResponse])
async def get_my_reviews(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Customer sees only their own reviews."""
    service = ReviewService(db)
    return await service.get_my_reviews(current_user)


@router.get("", response_model=List[ReviewResponse])
async def get_all_reviews(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin),
):
    """Admin sees all reviews from all customers."""
    service = ReviewService(db)
    return await service.get_all_reviews(current_user)


@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: str,
    data: UpdateReviewRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Customer edits their own review."""
    service = ReviewService(db)
    return await service.update_review(review_id, data, current_user)


@router.delete("/{review_id}", status_code=204)
async def delete_review(
    review_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Customer deletes their own review. Admin can delete any review."""
    service = ReviewService(db)
    await service.delete_review(review_id, current_user)