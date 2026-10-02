"""
Database bootstrap for the MVP.

Uses SQLite (file-based, zero-config, ships with Python) per Phase 2
Section 3.2. The schema below matches Phase 2 Section 3.3 exactly.
Swapping to Postgres/MySQL later only means changing this module and
the repository layer's connection handling -- services never touch
SQL directly.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "store.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('buyer', 'seller'))
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id INTEGER NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    price REAL NOT NULL,
    stock_qty INTEGER NOT NULL DEFAULT 0,
    image_path TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_id INTEGER NOT NULL REFERENCES users(id),
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending', 'shipped', 'delivered', 'cancelled')),
    total REAL NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL
);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(seed: bool = True) -> None:
    """Create tables if they don't exist, and seed demo data for the MVP demo."""
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()

    if seed:
        _seed_demo_data(conn)

    conn.close()


def _seed_demo_data(conn: sqlite3.Connection) -> None:
    from services.auth_service import hash_password

    existing = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]
    if existing > 0:
        return  # already seeded

    conn.execute(
        "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        ("SoleStep Store", "seller@example.com", hash_password("password123"), "seller"),
    )
    conn.execute(
        "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        ("Demo Buyer", "buyer@example.com", hash_password("password123"), "buyer"),
    )
    seller_id = conn.execute(
        "SELECT id FROM users WHERE email = ?", ("seller@example.com",)
    ).fetchone()["id"]

    demo_products = [
        ("Classic White Sneakers", "Everyday low-top sneakers in clean white leather.", 49.99, 20),
        ("Men's Running Trainers", "Lightweight mesh trainers built for daily runs.", 65.00, 15),
        ("Leather Oxford Shoes", "Formal brown leather oxfords with a stitched sole.", 89.99, 3),
        ("Suede Ankle Boots", "Chelsea-style suede ankle boots with elastic side panels.", 74.50, 10),
        ("Canvas High-Top Sneakers", "Classic canvas high-tops in navy blue.", 39.99, 25),
        ("Slide Sandals", "Cushioned slide sandals for everyday wear.", 19.99, 40),
    ]
    for name, desc, price, stock in demo_products:
        conn.execute(
            "INSERT INTO products (seller_id, name, description, price, stock_qty) "
            "VALUES (?, ?, ?, ?, ?)",
            (seller_id, name, desc, price, stock),
        )
    conn.commit()
