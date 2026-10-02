# SoleStep — Shoe Store MVP (Phase 3: Development)

A working prototype implementing the Phase 1 (Analysis) requirements and
Phase 2 (Design) wireframes/architecture, built as a single Python codebase
with [Flet](https://flet.dev). SoleStep is a shoe store: sellers list shoes,
buyers browse, cart, and check out.

## What's implemented

| Screen (Phase 2 wireframe) | File | Requirement |
|---|---|---|
| Login / Register | `views/login_view.py` | FR-1 |
| Home / Product List | `views/home_view.py` | FR-2 |
| Product Detail | `views/product_detail_view.py` | FR-2, FR-3 |
| Cart | `views/cart_view.py` | FR-3 |
| Checkout + Confirmation | `views/checkout_view.py` | FR-4 |
| Seller Dashboard (products + orders) | `views/seller_dashboard_view.py` | FR-1, FR-5, FR-7 |

Backend layers (Phase 2 Section 3):
- `models.py` — data structures (User, Product, CartItem, Order, OrderItem)
- `db.py` — SQLite schema + demo shoe catalog seeding
- `repositories.py` — data access layer (all SQL lives here)
- `services/` — business logic (auth, catalog, cart, order/checkout + stock validation)
- `assets/logo.png`, `assets/logo_icon.png` — SoleStep brand assets, loaded via Flet's `assets_dir`

## Run it

```bash
pip install -r requirements.txt

# Desktop window:
flet run main.py

# Or in a browser:
flet run --web main.py
```

On first run, `main.py` calls `init_db(seed=True)`, which creates
`store.db` (SQLite) and seeds two demo accounts and a six-item shoe catalog.

**Demo accounts** (password for both: `password123`):
- `seller@example.com` — Seller Dashboard (manage shoe listings/orders)
- `buyer@example.com` — Buyer flow (browse → cart → checkout)

**Demo catalog:** Classic White Sneakers, Men's Running Trainers, Leather
Oxford Shoes (seeded low-stock, qty 3 — good for testing the stock-validation
path), Suede Ankle Boots, Canvas High-Top Sneakers, Slide Sandals.

## Verifying the logic without a display

`test_logic.py` exercises the DB/repository/service layers directly
(no UI required) — registration, login, catalog CRUD, cart totals,
checkout with stock validation, overselling rejection, and the
forward-only order status workflow. The `tests/` directory has the
full 29-case automated suite used in Phase 4:

```bash
python3 -m unittest discover -s tests -v
```

## Known MVP limitations (deferred to production-ready phase)

- Password hashing uses a static salt (fine for a demo, not production).
- No real payment gateway integration — checkout captures a payment
  *method* only.
- SQLite is single-file/local; Phase 2 Section 3.2 notes the repository
  layer is structured so this can move to a hosted Postgres/MySQL
  instance without changing services or views.
- No automated UI tests (Flet apps need a running display); logic is
  covered by the `tests/` suite instead.
- Product photos are placeholder icons in this MVP — real shoe photography
  is a production follow-up (`image_path` is already in the schema).
