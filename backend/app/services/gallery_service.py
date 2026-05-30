import cloudinary
import cloudinary.uploader
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.gallery_repository import GalleryRepository
from app.schemas.gallery import AddGalleryItemRequest, UpdateCaptionRequest, GalleryItemResponse
from app.models.user import UserModel
from app.core.config import settings
from app.core.exceptions import NotFoundException
from app.services.audit_log_service import audit


def _configure_cloudinary():
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
    )


def _to_response(item) -> GalleryItemResponse:
    return GalleryItemResponse(
        id=item.id, image_url=item.image_url, public_id=item.public_id,
        caption=item.caption, uploaded_by=item.uploaded_by,
        uploaded_by_name=item.uploaded_by_name, created_at=item.created_at,
    )


class GalleryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = GalleryRepository(db)
        self.db = db

    async def add_item(self, data: AddGalleryItemRequest, current_user: UserModel) -> GalleryItemResponse:
        doc = {
            "image_url": data.image_url, "public_id": data.public_id,
            "caption": data.caption, "uploaded_by": current_user.id,
            "uploaded_by_name": current_user.name,
        }
        item = await self.repo.create(doc)
        await audit(
            db=self.db, actor_id=current_user.id, actor_name=current_user.name,
            actor_role=current_user.role, action="gallery_photo_uploaded",
            description=f"Photo uploaded to gallery" + (f": \"{data.caption}\"" if data.caption else ""),
            entity_type="gallery", entity_id=item.id,
        )
        return _to_response(item)

    async def get_all(self) -> List[GalleryItemResponse]:
        return [_to_response(i) for i in await self.repo.find_all()]

    async def update_caption(self, item_id: str, data: UpdateCaptionRequest, current_user: UserModel) -> GalleryItemResponse:
        item = await self.repo.update_caption(item_id, data.caption)
        if not item:
            raise NotFoundException("Gallery item")
        await audit(
            db=self.db, actor_id=current_user.id, actor_name=current_user.name,
            actor_role=current_user.role, action="gallery_caption_updated",
            description=f"Gallery photo caption updated: \"{data.caption}\"",
            entity_type="gallery", entity_id=item_id,
        )
        return _to_response(item)

    async def delete_item(self, item_id: str, current_user: UserModel) -> dict:
        item = await self.repo.find_by_id(item_id)
        if not item:
            raise NotFoundException("Gallery item")
        try:
            _configure_cloudinary()
            cloudinary.uploader.destroy(item.public_id)
        except Exception:
            pass
        await self.repo.delete(item_id)
        await audit(
            db=self.db, actor_id=current_user.id, actor_name=current_user.name,
            actor_role=current_user.role, action="gallery_photo_deleted",
            description=f"Gallery photo deleted" + (f": \"{item.caption}\"" if item.caption else ""),
            entity_type="gallery", entity_id=item_id,
        )
        return {"message": "Photo deleted successfully."}