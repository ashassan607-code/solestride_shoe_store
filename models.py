"""
Core data structures for the SoleStep shoe store MVP.

These map 1:1 to the Phase 2 design (Section 2.1 Core Data Structures /
Section 3.3 Database Schema). Kept as plain dataclasses for the MVP;
an ORM can replace these later without changing the service layer,
since services only depend on these shapes, not on how they're stored.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class User:
    id: Optional[int]
    name: str
    email: str
    password_hash: str
    role: str  # "buyer" | "seller"


@dataclass
class Product:
    id: Optional[int]
    seller_id: int
    name: str
    description: str
    price: float
    stock_qty: int
    image_path: str = ""


@dataclass
class CartItem:
    product_id: int
    quantity: int


@dataclass
class Order:
    id: Optional[int]
    buyer_id: int
    status: str  # "pending" | "shipped" | "delivered" | "cancelled"
    total: float
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class OrderItem:
    id: Optional[int]
    order_id: int
    product_id: int
    quantity: int
    unit_price: float  # snapshot of Product.price at purchase time
