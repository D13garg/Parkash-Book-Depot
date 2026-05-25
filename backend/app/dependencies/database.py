from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import get_database


async def get_db() -> AsyncIOMotorDatabase:
    """
    FastAPI dependency — inject MongoDB database into any route.

    Usage:
        @router.get("/example")
        async def example(db: AsyncIOMotorDatabase = Depends(get_db)):
            ...
    """
    return get_database()
