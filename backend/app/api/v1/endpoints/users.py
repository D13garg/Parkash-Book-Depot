from typing import List
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from bson import ObjectId

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import UserModel
from app.schemas.user import UserResponse
from app.core.exceptions import NotFoundException, BadRequestException
from app.services.audit_log_service import audit

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


@router.get("", response_model=List[UserResponse])
async def get_all_users(
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: UserModel = Depends(get_current_admin),
):
    """Returns all users (customers + associates). Admin only."""
    cursor = db["users"].find({})
    docs = await cursor.to_list(length=None)
    users = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        users.append(UserResponse(
            id=doc["_id"], name=doc["name"], email=doc["email"],
            role=doc["role"], is_active=doc["is_active"],
            phone=doc.get("phone"), address=doc.get("address"),
            created_at=doc["created_at"], updated_at=doc["updated_at"],
        ))
    return users


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin),
):
    """Deactivate a user account. Admin only. Cannot deactivate yourself."""
    if user_id == current_admin.id:
        raise BadRequestException("You cannot deactivate your own account.")

    doc = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not doc:
        raise NotFoundException("User")

    await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc)}}
    )
    doc["_id"] = str(doc["_id"])
    doc["is_active"] = False

    await audit(
        db=db, actor_id=current_admin.id, actor_name=current_admin.name,
        actor_role=current_admin.role, action="user_deactivated",
        description=f"Admin deactivated user: {doc['name']} ({doc['email']})",
        entity_type="user", entity_id=user_id,
    )
    return UserResponse(**{k: doc[k] for k in ["id","name","email","role","is_active","phone","address","created_at","updated_at"] if k in doc}, id=doc["_id"])


@router.patch("/{user_id}/reactivate", response_model=UserResponse)
async def reactivate_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin),
):
    """Reactivate a deactivated user account. Admin only."""
    doc = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not doc:
        raise NotFoundException("User")

    await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": True, "updated_at": datetime.now(timezone.utc)}}
    )
    doc["_id"] = str(doc["_id"])
    doc["is_active"] = True

    await audit(
        db=db, actor_id=current_admin.id, actor_name=current_admin.name,
        actor_role=current_admin.role, action="user_reactivated",
        description=f"Admin reactivated user: {doc['name']} ({doc['email']})",
        entity_type="user", entity_id=user_id,
    )
    return UserResponse(id=doc["_id"], name=doc["name"], email=doc["email"],
        role=doc["role"], is_active=doc["is_active"], phone=doc.get("phone"),
        address=doc.get("address"), created_at=doc["created_at"], updated_at=doc["updated_at"])