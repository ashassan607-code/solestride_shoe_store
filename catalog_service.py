"""
Catalog service -- Phase 2 Section 3.1, maps to Phase 1 FR-1, FR-2, FR-7.
"""
import os
import sys
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Product
from repositories import ProductRepository

LOW_STOCK_THRESHOLD = 5


def list_products(search: str = "") -> List[Product]:
    """Buyer-facing browse/search (FR-2)."""
    return ProductRepository().list_all(search=search)


def get_product(product_id: int) -> Product:
    product = ProductRepository().get_by_id(product_id)
    if not product:
        raise ValueError("Product not found.")
    return product


def list_seller_products(seller_id: int) -> List[Product]:
    """Seller dashboard catalog view, with low-stock flag (FR-7)."""
    return ProductRepository().list_by_seller(seller_id)


def is_low_stock(product: Product) -> bool:
    return product.stock_qty <= LOW_STOCK_THRESHOLD


def upsert_product(seller_id: int, product_id, name: str, description: str,
                    price: float, stock_qty: int, image_path: str = "") -> Product:
    """Create or edit a product (FR-1)."""
    if price < 0 or stock_qty < 0:
        raise ValueError("Price and stock must be non-negative.")
    product = Product(
        id=product_id, seller_id=seller_id, name=name, description=description,
        price=price, stock_qty=stock_qty, image_path=image_path,
    )
    return ProductRepository().upsert(product)


def delete_product(product_id: int) -> None:
    ProductRepository().delete(product_id)
