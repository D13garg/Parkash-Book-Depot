from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_admin
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import AnalyticsResponse
from app.models.user import UserModel

router = APIRouter()


@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: UserModel = Depends(get_current_admin),
):
    """
    Full operational analytics dashboard.
    Admin only. Pure aggregation — no new collections.
    """
    return await AnalyticsService(db).get_analytics()