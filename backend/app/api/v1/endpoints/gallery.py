from typing import List
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user, get_current_admin
from app.services.gallery_service import GalleryService
from app.schemas.gallery import AddGalleryItemRequest, UpdateCaptionRequest, GalleryItemResponse
from app.models.user import UserModel

router = APIRouter()


@router.get("", response_model=List[GalleryItemResponse])
async def get_gallery(
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return await GalleryService(db).get_all()


@router.post("", response_model=GalleryItemResponse, status_code=201)
async def add_photo(
    data: AddGalleryItemRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin),
):
    return await GalleryService(db).add_item(data, current_user)


@router.patch("/{item_id}/caption", response_model=GalleryItemResponse)
async def update_caption(
    item_id: str, data: UpdateCaptionRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin),
):
    return await GalleryService(db).update_caption(item_id, data, current_user)


@router.delete("/{item_id}")
async def delete_photo(
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin),
):
    return await GalleryService(db).delete_item(item_id, current_user)