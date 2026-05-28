from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AddGalleryItemRequest(BaseModel):
    image_url: str = Field(..., min_length=1)
    public_id: str = Field(..., min_length=1)
    caption: Optional[str] = None


class UpdateCaptionRequest(BaseModel):
    caption: str = Field(..., min_length=1, max_length=300)


class GalleryItemResponse(BaseModel):
    id: str
    image_url: str
    public_id: str
    caption: Optional[str] = None
    uploaded_by: str
    uploaded_by_name: str
    created_at: datetime