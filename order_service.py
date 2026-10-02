"""
Order service -- Phase 2 Section 3.1, maps to Phase 1 FR-4, FR-5.

Implements the stock-validation algorithm and the linear order-status
workflow defined in Phase 2 Section 2.2 / 2.3.
"""
import os
import sys
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Order, OrderItem
from repositories import OrderRepository, ProductRepository
from services.cart_service import CartService

DELIVERY_FEE = 3.00

STATUS_FLOW = {
    "pending": ["shipped", "cancelled"],
    "shipped": ["delivered"],
    "delivered": [],
    "cancelled": [],
}


def checkout(buyer_id: int, cart: CartService) -> Order:
    """
    Validates stock for every cart line, then creates the order.
    Raises ValueError (with the offending product names) instead of
    silently failing the whole order, per Phase 2 Section 2.2.
    """
    items = cart.get_items()
    if not items:
        raise ValueError("Cart is empty.")

    product_repo = ProductRepository()
    problems = []
    order_items: List[OrderItem] = []
    total = 0.0

    for cart_item in items:
        product = product_repo.get_by_id(cart_item.product_id)
        if not product:
            problems.append(f"Product #{cart_item.product_id} no longer exists.")
            continue
        if cart_item.quantity > product.stock_qty:
            problems.append(
                f"'{product.name}' only has {product.stock_qty} left "
                f"(you requested {cart_item.quantity})."
            )
            continue
        order_items.append(OrderItem(
            id=None, order_id=None, product_id=product.id,
            quantity=cart_item.quantity, unit_price=product.price,
        ))
        total += product.price * cart_item.quantity

    if problems:
        raise ValueError(" ".join(problems))

    total = round(total + DELIVERY_FEE, 2)
    order = Order(id=None, buyer_id=buyer_id, status="pending", total=total)
    order = OrderRepository().create_with_items(order, order_items)
    cart.clear()
    return order


def list_seller_orders(seller_id: int) -> List[dict]:
    return OrderRepository().list_by_seller(seller_id)


def advance_status(order_id: int, current_status: str, new_status: str) -> None:
    """Enforces forward-only transitions (Phase 2 Section 2.2)."""
    allowed = STATUS_FLOW.get(current_status, [])
    if new_status not in allowed:
        raise ValueError(f"Cannot move order from '{current_status}' to '{new_status}'.")
    OrderRepository().update_status(order_id, new_status)
