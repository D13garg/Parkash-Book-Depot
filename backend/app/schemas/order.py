from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class OrderItemRequest(BaseModel):
    book_id: str
    quantity: int = Field(..., ge=1)


class PlaceOrderRequest(BaseModel):
    items: List[OrderItemRequest] = Field(..., min_length=1)
    delivery_address: str = Field(..., min_length=5)
    phone: str = Field(..., min_length=10)
    notes: Optional[str] = None


class UpdateOrderStatusRequest(BaseModel):
    status: str


class OrderItemResponse(BaseModel):
    book_id: str
    title: str
    price: float
    quantity: int
    subtotal: float


class OrderResponse(BaseModel):
    id: str
    customer_id: str
    customer_name: str
    items: List[OrderItemResponse]
    total_amount: float
    status: str
    delivery_address: str
    phone: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime