from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, Any
from datetime import datetime, timezone
from bson import ObjectId
from app.core.enums import UserRole


class UserModel(BaseModel):
    """
    Represents a user document as stored in MongoDB.
    This is NOT what the API returns — see schemas/user.py for that.
    """
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    email: EmailStr
    hashed_password: str
    role: UserRole = UserRole.CUSTOMER
    is_active: bool = True
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, ObjectId):
            return str(v)
        return str(v)

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, v: Any) -> UserRole:
        if isinstance(v, UserRole):
            return v
        return UserRole(str(v))

    model_config = {
        "populate_by_name": True,
    }
