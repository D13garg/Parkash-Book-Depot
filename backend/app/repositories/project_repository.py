from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional
from datetime import datetime, timezone

from app.models.project import ProjectModel

COLLECTION = "projects"


class ProjectRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION]

    def _doc_to_model(self, doc: dict) -> ProjectModel:
        doc["_id"] = str(doc["_id"])
        return ProjectModel(**doc)

    async def create(self, data: dict) -> ProjectModel:
        result = await self.collection.insert_one(data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        return self._doc_to_model(doc)

    async def find_by_id(self, project_id: str) -> Optional[ProjectModel]:
        if not ObjectId.is_valid(project_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(project_id)})
        return self._doc_to_model(doc) if doc else None

    async def find_all(
        self,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[ProjectModel], int]:
        """Admin view — returns all projects."""
        query = {}
        if status:
            query["status"] = status
        total = await self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._doc_to_model(d) for d in docs], total

    async def find_by_associate(
        self,
        associate_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[ProjectModel], int]:
        """Associate view — only returns projects assigned to them."""
        query = {"assigned_to": associate_id}
        if status:
            query["status"] = status
        total = await self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._doc_to_model(d) for d in docs], total

    async def update(self, project_id: str, update_data: dict) -> Optional[ProjectModel]:
        update_data["updated_at"] = datetime.now(timezone.utc)
        await self.collection.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": update_data}
        )
        return await self.find_by_id(project_id)

    async def assign_associate(self, project_id: str, associate_id: str) -> Optional[ProjectModel]:
        return await self.update(project_id, {
            "assigned_to": associate_id,
            "status": "assigned",
        })
