from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone


class OrderItemModel(BaseModel):
    book_id: str
    title: str
    price: float
    quantity: int
    subtotal: float


class OrderModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    customer_id: str
    customer_name: str
    items: List[OrderItemModel]
    total_amount: float
    status: str = "pending"
    delivery_address: str
    phone: str
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True