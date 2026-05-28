from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


class GalleryItemModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    image_url: str                      # Cloudinary URL
    public_id: str                      # Cloudinary public_id — needed for deletion
    caption: Optional[str] = None
    uploaded_by: str                    # admin user id
    uploaded_by_name: str               # admin name — denormalised
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True