from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.schemas.review import (
    ReviewCreate,
    ReviewResponse,
)

from app.repositories.review_repository import (
    ReviewRepository,
)

from app.services.review_service import (
    ReviewService,
)

from app.core.database import get_database

from app.dependencies.auth import (
    get_current_user,
)

router = APIRouter()


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    payload: ReviewCreate,
):
    db = get_database()

    repository = ReviewRepository(db)

    service = ReviewService(repository)

    return await service.create_review(
        payload
    )


@router.get(
    "",
    response_model=List[ReviewResponse],
)
async def get_reviews(
    current_user=Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    db = get_database()

    repository = ReviewRepository(db)

    service = ReviewService(repository)

    return await service.get_reviews()