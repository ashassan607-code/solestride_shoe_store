"""
Cart service -- Phase 2 Section 2.1 / 2.2, maps to Phase 1 FR-3.

The cart is per-session, in-memory state (Phase 2 note: "held in
session/local state until checkout"). One CartService instance is
created per connected Flet client in main.py -- it is NOT a global,
so two buyers never share a cart.
"""
import os
import sys
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import CartItem
from services import catalog_service


class CartService:
    def __init__(self):
        self._items: Dict[int, CartItem] = {}  # product_id -> CartItem

    def add_item(self, product_id: int, quantity: int = 1) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        if product_id in self._items:
            self._items[product_id].quantity += quantity
        else:
            self._items[product_id] = CartItem(product_id=product_id, quantity=quantity)

    def update_quantity(self, product_id: int, quantity: int) -> None:
        if quantity <= 0:
            self.remove_item(product_id)
            return
        if product_id in self._items:
            self._items[product_id].quantity = quantity

    def remove_item(self, product_id: int) -> None:
        self._items.pop(product_id, None)

    def clear(self) -> None:
        self._items.clear()

    def get_items(self) -> List[CartItem]:
        return list(self._items.values())

    def get_items_with_products(self) -> List[dict]:
        """Cart items joined with live product data, for rendering."""
        out = []
        for item in self._items.values():
            product = catalog_service.get_product(item.product_id)
            out.append({"item": item, "product": product})
        return out

    def subtotal(self) -> float:
        """Phase 2 Section 2.2: total = sum(unit_price * quantity)."""
        total = 0.0
        for item in self._items.values():
            product = catalog_service.get_product(item.product_id)
            total += product.price * item.quantity
        return round(total, 2)
