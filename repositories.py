"""
Data access layer -- Phase 2 Section 3.2.

Every database read/write goes through these repository classes.
The service layer never writes raw SQL; it calls repository methods.
This is the seam that lets the MVP move off SQLite later without
touching services or the UI.
"""
from typing import List, Optional
from db import get_connection
from models import User, Product, Order, OrderItem


class UserRepository:
    def create(self, user: User) -> User:
        conn = get_connection()
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (user.name, user.email, user.password_hash, user.role),
        )
        conn.commit()
        user.id = cur.lastrowid
        conn.close()
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        conn = get_connection()
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        return self._to_user(row) if row else None

    def get_by_id(self, user_id: int) -> Optional[User]:
        conn = get_connection()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return self._to_user(row) if row else None

    @staticmethod
    def _to_user(row) -> User:
        return User(id=row["id"], name=row["name"], email=row["email"],
                     password_hash=row["password_hash"], role=row["role"])


class ProductRepository:
    def list_all(self, search: str = "") -> List[Product]:
        conn = get_connection()
        if search:
            rows = conn.execute(
                "SELECT * FROM products WHERE name LIKE ? ORDER BY id DESC",
                (f"%{search}%",),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
        conn.close()
        return [self._to_product(r) for r in rows]

    def list_by_seller(self, seller_id: int) -> List[Product]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM products WHERE seller_id = ? ORDER BY id DESC", (seller_id,)
        ).fetchall()
        conn.close()
        return [self._to_product(r) for r in rows]

    def get_by_id(self, product_id: int) -> Optional[Product]:
        conn = get_connection()
        row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        conn.close()
        return self._to_product(row) if row else None

    def upsert(self, product: Product) -> Product:
        conn = get_connection()
        if product.id is None:
            cur = conn.execute(
                "INSERT INTO products (seller_id, name, description, price, stock_qty, image_path) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (product.seller_id, product.name, product.description,
                 product.price, product.stock_qty, product.image_path),
            )
            product.id = cur.lastrowid
        else:
            conn.execute(
                "UPDATE products SET name=?, description=?, price=?, stock_qty=?, image_path=? "
                "WHERE id=?",
                (product.name, product.description, product.price,
                 product.stock_qty, product.image_path, product.id),
            )
        conn.commit()
        conn.close()
        return product

    def delete(self, product_id: int) -> None:
        conn = get_connection()
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()

    def decrement_stock(self, product_id: int, quantity: int, conn=None) -> None:
        owns_conn = conn is None
        conn = conn or get_connection()
        conn.execute(
            "UPDATE products SET stock_qty = stock_qty - ? WHERE id = ?",
            (quantity, product_id),
        )
        if owns_conn:
            conn.commit()
            conn.close()

    @staticmethod
    def _to_product(row) -> Product:
        return Product(id=row["id"], seller_id=row["seller_id"], name=row["name"],
                        description=row["description"], price=row["price"],
                        stock_qty=row["stock_qty"], image_path=row["image_path"])


class OrderRepository:
    def create_with_items(self, order: Order, items: List[OrderItem]) -> Order:
        """Creates the order and its line items, and decrements stock,
        all in a single transaction (Phase 2 Section 2.2 stock validation)."""
        conn = get_connection()
        try:
            cur = conn.execute(
                "INSERT INTO orders (buyer_id, status, total, created_at) VALUES (?, ?, ?, ?)",
                (order.buyer_id, order.status, order.total, order.created_at),
            )
            order.id = cur.lastrowid
            for item in items:
                conn.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, unit_price) "
                    "VALUES (?, ?, ?, ?)",
                    (order.id, item.product_id, item.quantity, item.unit_price),
                )
                ProductRepository().decrement_stock(item.product_id, item.quantity, conn=conn)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return order

    def list_by_seller(self, seller_id: int) -> List[dict]:
        """Orders containing at least one product from this seller."""
        conn = get_connection()
        rows = conn.execute(
            """
            SELECT DISTINCT o.* FROM orders o
            JOIN order_items oi ON oi.order_id = o.id
            JOIN products p ON p.id = oi.product_id
            WHERE p.seller_id = ?
            ORDER BY o.id DESC
            """,
            (seller_id,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_status(self, order_id: int, status: str) -> None:
        conn = get_connection()
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        conn.commit()
        conn.close()
