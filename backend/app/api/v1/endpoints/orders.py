from typing import Optional
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user, get_current_admin
from app.services.order_service import OrderService
from app.schemas.order import PlaceOrderRequest, UpdateOrderStatusRequest, OrderResponse
from app.schemas.book import PaginatedResponse
from app.models.user import UserModel

router = APIRouter()


@router.post("", response_model=OrderResponse, status_code=201)
async def place_order(
    data: PlaceOrderRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return await OrderService(db).place_order(data, current_user)


@router.get("/mine", response_model=PaginatedResponse[OrderResponse])
async def get_my_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return await OrderService(db).get_my_orders(current_user, page, page_size)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return await OrderService(db).get_order(order_id, current_user)


@router.get("", response_model=PaginatedResponse[OrderResponse])
async def get_all_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = Query(default=None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: UserModel = Depends(get_current_admin),
):
    return await OrderService(db).get_all_orders(status, page, page_size)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    data: UpdateOrderStatusRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin),
):
    return await OrderService(db).update_status(order_id, data, current_user)