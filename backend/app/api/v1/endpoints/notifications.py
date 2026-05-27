from typing import List
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.services.notification_service import NotificationService
from app.schemas.notification import NotificationResponse, UnreadCountResponse
from app.models.user import UserModel

router = APIRouter()


@router.get("", response_model=List[NotificationResponse])
async def get_my_notifications(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    service = NotificationService(db)
    return await service.get_my_notifications(current_user.id)


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    service = NotificationService(db)
    return await service.get_unread_count(current_user.id)


@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    service = NotificationService(db)
    await service.mark_read(notification_id, current_user.id)
    return {"message": "Marked as read."}


@router.patch("/read-all")
async def mark_all_read(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    service = NotificationService(db)
    await service.mark_all_read(current_user.id)
    return {"message": "All notifications marked as read."}