"""Demo data so the MVP opens with a populated store. Safe to call repeatedly."""
from __future__ import annotations

from . import db
from .repositories import ProductRepository, UserRepository
from .services import auth_service, cart_service, order_service

DEMO_SELLER = ("SoleStride Store", "seller@solestride.com", "Seller@123")
DEMO_BUYER = ("Amina Yusuf", "buyer@solestride.com", "Buyer@123")

# name, category, price (NGN), image, description, stock per EU size 39..45
_PRODUCTS = [
    ("Classic Runner", "Sneakers", 28500, "shoes/classic_runner.png",
     "Lightweight everyday running shoe with a cushioned sole and breathable mesh upper.",
     {39: 4, 40: 6, 41: 8, 42: 10, 43: 6, 44: 3, 45: 2}),
    ("Oxford Leather", "Formal", 45000, "shoes/oxford_leather.png",
     "Handstitched leather oxford for the office, weddings and every formal occasion.",
     {39: 0, 40: 2, 41: 4, 42: 3, 43: 5, 44: 4, 45: 1}),
    ("Slide Sandal", "Sandals", 9800, "shoes/slide_sandal.png",
     "Soft, flexible slide sandal. Easy to slip on, easy to clean.",
     {39: 10, 40: 12, 41: 15, 42: 14, 43: 12, 44: 8, 45: 6}),
    ("Court Sneaker", "Sneakers", 32000, "shoes/court_sneaker.png",
     "Clean white court sneaker that goes with everything.",
     {39: 3, 40: 5, 41: 7, 42: 9, 43: 7, 44: 4, 45: 0}),
    ("Chelsea Boot", "Boots", 52500, "shoes/chelsea_boot.png",
     "Elastic-sided leather boot with a durable grip sole.",
     {39: 0, 40: 3, 41: 4, 42: 5, 43: 4, 44: 2, 45: 1}),
    ("Sport Trainer", "Sneakers", 38000, "shoes/sport_trainer.png",
     "High-support trainer built for gym sessions and long days on your feet.",
     {39: 2, 40: 4, 41: 6, 42: 8, 43: 6, 44: 5, 45: 3}),
    ("Classic Loafer", "Formal", 41000, "shoes/classic_loafer.png",
     "Slip-on leather loafer: smart enough for work, relaxed enough for weekends.",
     {39: 3, 40: 4, 41: 6, 42: 6, 43: 5, 44: 3, 45: 2}),
    ("Strap Sandal", "Sandals", 12500, "shoes/strap_sandal.png",
     "Adjustable strap sandal with a contoured footbed for all-day comfort.",
     {39: 6, 40: 8, 41: 9, 42: 9, 43: 7, 44: 5, 45: 4}),
]


def seed_demo_data() -> None:
    with db.get_conn() as conn:
        if UserRepository(conn).count() > 0:
            return
    seller = auth_service.register(*DEMO_SELLER[:3], role="seller")
    buyer = auth_service.register(*DEMO_BUYER[:3], role="buyer")
    with db.get_conn() as conn:
        repo = ProductRepository(conn)
        for name, cat, price, img, desc, sizes in _PRODUCTS:
            pid = repo.insert(seller.id, name, desc, price, cat, img)
            for size, qty in sizes.items():
                repo.set_size_stock(pid, size, qty)
    # one sample order so the seller dashboard is not empty on first run
    cart = cart_service.Cart()
    cart_service.add_item(cart, 1, 42, 1)
    cart_service.add_item(cart, 3, 41, 2)
    order_service.checkout(buyer.id, cart, {
        "name": buyer.name, "phone": "08031234567",
        "address": "12 Jimeta Road, Yola, Adamawa", "payment_method": "pay_on_delivery",
    })
