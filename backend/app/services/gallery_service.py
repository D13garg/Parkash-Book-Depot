import cloudinary
import cloudinary.uploader
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.gallery_repository import GalleryRepository
from app.schemas.gallery import AddGalleryItemRequest, UpdateCaptionRequest, GalleryItemResponse
from app.models.user import UserModel
from app.core.config import settings
from app.core.exceptions import NotFoundException


def _configure_cloudinary():
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
    )


def _to_response(item) -> GalleryItemResponse:
    return GalleryItemResponse(
        id=item.id,
        image_url=item.image_url,
        public_id=item.public_id,
        caption=item.caption,
        uploaded_by=item.uploaded_by,
        uploaded_by_name=item.uploaded_by_name,
        created_at=item.created_at,
    )


class GalleryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = GalleryRepository(db)

    async def add_item(
        self, data: AddGalleryItemRequest, current_user: UserModel
    ) -> GalleryItemResponse:
        doc = {
            "image_url": data.image_url,
            "public_id": data.public_id,
            "caption": data.caption,
            "uploaded_by": current_user.id,
            "uploaded_by_name": current_user.name,
        }
        item = await self.repo.create(doc)
        return _to_response(item)

    async def get_all(self) -> List[GalleryItemResponse]:
        items = await self.repo.find_all()
        return [_to_response(i) for i in items]

    async def update_caption(
        self, item_id: str, data: UpdateCaptionRequest
    ) -> GalleryItemResponse:
        item = await self.repo.update_caption(item_id, data.caption)
        if not item:
            raise NotFoundException("Gallery item")
        return _to_response(item)

    async def delete_item(self, item_id: str) -> dict:
        # First get the item to find the Cloudinary public_id
        item = await self.repo.find_by_id(item_id)
        if not item:
            raise NotFoundException("Gallery item")

        # Delete from Cloudinary
        try:
            _configure_cloudinary()
            cloudinary.uploader.destroy(item.public_id)
        except Exception:
            pass  # If Cloudinary deletion fails, still remove from DB

        # Delete from MongoDB
        await self.repo.delete(item_id)
        return {"message": "Photo deleted successfully."}