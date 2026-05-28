from typing import List
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import UserModel
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/associates", response_model=List[UserResponse])
async def get_associates(
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: UserModel = Depends(get_current_admin),
):
    """
    Returns all active associate accounts.
    Admin only — used to populate the assign dropdown.
    """
    cursor = db["users"].find({"role": "associate", "is_active": True})
    docs = await cursor.to_list(length=None)

    associates = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        associates.append(UserResponse(
            id=doc["_id"],
            name=doc["name"],
            email=doc["email"],
            role=doc["role"],
            is_active=doc["is_active"],
            phone=doc.get("phone"),
            address=doc.get("address"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        ))

    return associates