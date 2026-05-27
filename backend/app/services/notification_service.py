from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional

from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationResponse, UnreadCountResponse
from app.models.notification import NotificationModel


def _to_response(n: NotificationModel) -> NotificationResponse:
    return NotificationResponse(
        id=n.id,
        user_id=n.user_id,
        type=n.type,
        message=n.message,
        link=n.link,
        is_read=n.is_read,
        created_at=n.created_at,
    )


async def notify(
    db: AsyncIOMotorDatabase,
    user_id: str,
    type: str,
    message: str,
    link: Optional[str] = None,
) -> None:
    """
    Internal helper — called by other services to create a notification.
    Does not raise — notification failure should never break the main action.
    """
    try:
        repo = NotificationRepository(db)
        await repo.create({
            "user_id": user_id,
            "type": type,
            "message": message,
            "link": link,
            "is_read": False,
        })
    except Exception:
        pass  # silently ignore — notification is non-critical


async def notify_all_admins(
    db: AsyncIOMotorDatabase,
    type: str,
    message: str,
    link: Optional[str] = None,
) -> None:
    """Sends the same notification to every admin user."""
    try:
        repo = NotificationRepository(db)
        admin_ids = await repo.find_admins(db)
        for admin_id in admin_ids:
            await repo.create({
                "user_id": admin_id,
                "type": type,
                "message": message,
                "link": link,
                "is_read": False,
            })
    except Exception:
        pass


class NotificationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = NotificationRepository(db)

    async def get_my_notifications(self, user_id: str) -> List[NotificationResponse]:
        notifications = await self.repo.find_by_user(user_id)
        return [_to_response(n) for n in notifications]

    async def get_unread_count(self, user_id: str) -> UnreadCountResponse:
        count = await self.repo.unread_count(user_id)
        return UnreadCountResponse(count=count)

    async def mark_read(self, notification_id: str, user_id: str) -> None:
        await self.repo.mark_read(notification_id, user_id)

    async def mark_all_read(self, user_id: str) -> None:
        await self.repo.mark_all_read(user_id)