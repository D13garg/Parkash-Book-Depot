import math
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from app.repositories.order_repository import OrderRepository
from app.repositories.book_repository import BookRepository
from app.schemas.order import PlaceOrderRequest, UpdateOrderStatusRequest, OrderResponse
from app.schemas.book import PaginatedResponse
from app.models.order import OrderModel
from app.models.user import UserModel
from app.core.enums import OrderStatus, is_valid_order_transition
from app.core.exceptions import BadRequestException, NotFoundException, ForbiddenException, InvalidStateTransitionException
from app.permissions.role_permissions import is_admin
from app.services.notification_service import notify, notify_all_admins
from app.services.audit_log_service import audit


def _to_response(o: OrderModel) -> OrderResponse:
    return OrderResponse(
        id=o.id, customer_id=o.customer_id, customer_name=o.customer_name,
        items=[{
            "book_id": item.book_id, "title": item.title,
            "price": item.price, "quantity": item.quantity, "subtotal": item.subtotal,
        } for item in o.items],
        total_amount=o.total_amount, status=o.status,
        delivery_address=o.delivery_address, phone=o.phone,
        notes=o.notes, created_at=o.created_at, updated_at=o.updated_at,
    )


class OrderService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.order_repo = OrderRepository(db)
        self.book_repo  = BookRepository(db)
        self.db = db

    async def place_order(self, data: PlaceOrderRequest, current_user: UserModel) -> OrderResponse:
        order_items, total = [], 0.0
        for item in data.items:
            book = await self.book_repo.find_by_id(item.book_id)
            if not book:
                raise NotFoundException(f"Book '{item.book_id}'")
            if book.stock < item.quantity:
                raise BadRequestException(
                    f"Insufficient stock for '{book.title}'. Available: {book.stock}, requested: {item.quantity}"
                )
            subtotal = book.price * item.quantity
            total += subtotal
            order_items.append({
                "book_id": book.id, "title": book.title,
                "price": book.price, "quantity": item.quantity, "subtotal": subtotal,
            })
            # Atomic decrement — if another order grabbed the last copy between
            # our check above and this update, decrement_stock_atomic returns None
            updated_book = await self.book_repo.decrement_stock_atomic(book.id, item.quantity)
            if updated_book is None:
                raise BadRequestException(
                    f"'{book.title}' just went out of stock. Please refresh and try again."
                )

        order = await self.order_repo.create({
            "customer_id": current_user.id, "customer_name": current_user.name,
            "items": order_items, "total_amount": round(total, 2),
            "status": OrderStatus.PENDING.value,
            "delivery_address": data.delivery_address, "phone": data.phone, "notes": data.notes,
        })
        await notify_all_admins(
            db=self.db, type="order_placed",
            message=f"New order from {current_user.name} — ₹{order.total_amount:.2f} ({len(order_items)} items)",
            link="/admin/orders",
        )
        await audit(
            db=self.db, actor_id=current_user.id, actor_name=current_user.name,
            actor_role=current_user.role, action="order_placed",
            description=f"Order placed for ₹{order.total_amount:.2f}",
            entity_type="order", entity_id=order.id,
            metadata={"total": order.total_amount, "items": len(order_items)},
        )
        return _to_response(order)

    async def get_my_orders(self, current_user: UserModel, page=1, page_size=20):
        skip = (page - 1) * page_size
        orders, total = await self.order_repo.find_by_customer(current_user.id, skip, page_size)
        return PaginatedResponse(
            items=[_to_response(o) for o in orders], total=total, page=page,
            page_size=page_size, total_pages=math.ceil(total/page_size) if total > 0 else 1,
        )

    async def get_order(self, order_id: str, current_user: UserModel) -> OrderResponse:
        order = await self.order_repo.find_by_id(order_id)
        if not order: raise NotFoundException("Order")
        if not is_admin(current_user) and order.customer_id != current_user.id:
            raise ForbiddenException()
        return _to_response(order)

    async def get_all_orders(self, status: Optional[str], page=1, page_size=20):
        skip = (page - 1) * page_size
        orders, total = await self.order_repo.find_all(status, skip, page_size)
        return PaginatedResponse(
            items=[_to_response(o) for o in orders], total=total, page=page,
            page_size=page_size, total_pages=math.ceil(total/page_size) if total > 0 else 1,
        )

    async def cancel_order(self, order_id: str, current_user: UserModel) -> OrderResponse:
        order = await self.order_repo.find_by_id(order_id)
        if not order:
            raise NotFoundException("Order")

        # Only the customer who placed it can cancel (admins use update_status)
        if order.customer_id != current_user.id:
            raise ForbiddenException()

        # Only pending or confirmed orders can be cancelled by customer
        if order.status not in [OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value]:
            raise BadRequestException(
                f"Orders in '{order.status}' status cannot be cancelled. "
                f"Only pending or confirmed orders can be cancelled."
            )

        # Atomically restore stock for every item
        for item in order.items:
            await self.book_repo.increment_stock_atomic(item.book_id, item.quantity)

        updated = await self.order_repo.update_status(order_id, OrderStatus.CANCELLED.value)

        await notify(
            db=self.db, user_id=order.customer_id, type="order_status_updated",
            message=f"Your order #{order_id[:8].upper()} has been cancelled and stock restored.",
            link="/customer/orders",
        )
        await audit(
            db=self.db, actor_id=current_user.id, actor_name=current_user.name,
            actor_role=current_user.role, action="order_cancelled",
            description=f"Customer cancelled order #{order_id[:8].upper()} — stock restored for {len(order.items)} item(s)",
            entity_type="order", entity_id=order_id,
            metadata={"total": order.total_amount, "items": len(order.items)},
        )
        return _to_response(updated)

    async def update_status(self, order_id: str, data: UpdateOrderStatusRequest, current_user: UserModel) -> OrderResponse:
        order = await self.order_repo.find_by_id(order_id)
        if not order: raise NotFoundException("Order")
        try:
            current = OrderStatus(order.status)
            new     = OrderStatus(data.status)
        except ValueError:
            raise BadRequestException(f"Invalid status: {data.status}")
        if not is_valid_order_transition(current, new):
            raise InvalidStateTransitionException(current=order.status, attempted=data.status)

        # If admin is cancelling, atomically restore stock for all items
        if new == OrderStatus.CANCELLED:
            for item in order.items:
                await self.book_repo.increment_stock_atomic(item.book_id, item.quantity)

        updated = await self.order_repo.update_status(order_id, data.status)
        await notify(
            db=self.db, user_id=order.customer_id, type="order_status_updated",
            message=f"Your order status updated to '{data.status}'", link="/customer/orders",
        )
        await audit(
            db=self.db, actor_id=current_user.id, actor_name=current_user.name,
            actor_role=current_user.role, action="order_status_updated",
            description=f"Order status: {order.status} → {data.status}",
            entity_type="order", entity_id=order_id,
            metadata={"old": order.status, "new": data.status},
        )
        return _to_response(updated)