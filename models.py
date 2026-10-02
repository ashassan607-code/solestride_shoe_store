"""Plain dataclasses used across the service and UI layers (Phase 2, section 2.1)."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class User:
    id: int
    name: str
    email: str
    role: str

    @property
    def is_seller(self) -> bool:
        return self.role == "seller"


@dataclass
class Product:
    id: int
    seller_id: int
    name: str
    description: str
    price: int
    category: str
    image_path: str
    is_active: bool = True
    sizes: dict[int, int] = field(default_factory=dict)  # size_eu -> stock_qty

    @property
    def total_stock(self) -> int:
        return sum(self.sizes.values())

    def stock_for(self, size: int) -> int:
        return self.sizes.get(size, 0)


@dataclass
class CartLine:
    product_id: int
    size_eu: int
    quantity: int
    name: str = ""
    image_path: str = ""
    unit_price: int = 0
    available: int = 0

    @property
    def line_total(self) -> int:
        return self.unit_price * self.quantity


@dataclass
class CartSummary:
    lines: list[CartLine]
    subtotal: int
    delivery_fee: int
    total: int

    @property
    def item_count(self) -> int:
        return sum(l.quantity for l in self.lines)


@dataclass
class OrderItem:
    product_id: int
    name: str
    size_eu: int
    quantity: int
    unit_price: int


@dataclass
class Order:
    id: int
    buyer_id: int
    buyer_name: str
    status: str
    total: int
    delivery_fee: int
    created_at: str
    status_updated_at: str
    shipping_name: str
    phone: str
    address: str
    payment_method: str
    items: list[OrderItem] = field(default_factory=list)

    @property
    def reference(self) -> str:
        return f"SS-{self.id:05d}"
