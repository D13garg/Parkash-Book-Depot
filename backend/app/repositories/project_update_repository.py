from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.models.project_update import ProjectUpdateModel

COLLECTION = "project_updates"


class ProjectUpdateRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION]

    def _doc_to_model(self, doc: dict) -> ProjectUpdateModel:
        doc["_id"] = str(doc["_id"])
        return ProjectUpdateModel(**doc)

    async def create(self, data: dict) -> ProjectUpdateModel:
        result = await self.collection.insert_one(data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        return self._doc_to_model(doc)

    async def find_by_project(self, project_id: str) -> list[ProjectUpdateModel]:
        """Returns all timeline entries for a project, oldest first."""
        cursor = self.collection.find(
            {"project_id": project_id}
        ).sort("created_at", 1)
        docs = await cursor.to_list(length=None)
        return [self._doc_to_model(d) for d in docs]
