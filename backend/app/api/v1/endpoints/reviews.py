from typing import List
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user, get_current_admin
from app.services.review_service import ReviewService
from app.schemas.review import CreateReviewRequest, ReviewResponse
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
    _: UserModel = Depends(get_current_admin),
    current_user: UserModel = Depends(get_current_user),
):
    """Admin sees all reviews from all customers."""
    service = ReviewService(db)
    return await service.get_all_reviews(current_user)