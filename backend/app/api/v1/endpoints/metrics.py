from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_admin
from app.services.metrics_service import MetricsService
from app.schemas.metrics import MetricsSummaryResponse, MetricsTrendResponse
from app.models.user import UserModel

router = APIRouter()


@router.get("/summary", response_model=MetricsSummaryResponse)
async def get_summary(
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: UserModel = Depends(get_current_admin),
):
    return await MetricsService(db).get_summary()


@router.get("/trend", response_model=MetricsTrendResponse)
async def get_trend(
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: UserModel = Depends(get_current_admin),
):
    return await MetricsService(db).get_trend()