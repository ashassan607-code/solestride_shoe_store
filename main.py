"""
Entry point for the SoleStep shoe store MVP (Phase 3: Development / Phase 5: Deployment).

Local run:
    flet run main.py         (desktop window)
    flet run --web main.py   (browser, http://localhost:8550)

Container / Azure run (see Dockerfile):
    FLET_WEB=true PORT=8000 python main.py
    -> serves as a web app on 0.0.0.0:$PORT, which is what Azure App
       Service for Containers expects (matched by WEBSITES_PORT).

Implements the screens designed in Phase 2 (Fig 1-5) on top of the
service/repository layers in services/ and repositories.py, backed by
the SQLite schema in db.py. Logo/brand assets live in assets/.
"""
import os

import flet as ft

from db import init_db
from services.cart_service import CartService

from views.login_view import build_login_view, build_register_view
from views.home_view import build_home_view
from views.product_detail_view import build_product_detail_view
from views.cart_view import build_cart_view
from views.checkout_view import build_checkout_view, build_order_confirmation_view
from views.seller_dashboard_view import build_seller_dashboard_view


class AppState:
    """Per-connection state: the logged-in user and their cart.
    A fresh AppState is created per client session (see main()) so
    concurrent buyers never share a cart or login session."""
    def __init__(self):
        self.current_user = None
        self.cart = CartService()


def main(page: ft.Page):
    page.title = "SoleStep — Shoe Store"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT

    app_state = AppState()

    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        route = page.route

        # Routes that don't require login
        if route == "/login":
            page.views.append(build_login_view(page, app_state))
        elif route == "/register":
            page.views.append(build_register_view(page, app_state))

        # Everything else requires a logged-in user
        elif app_state.current_user is None:
            page.go("/login")
            return

        elif route == "/":
            page.views.append(build_home_view(page, app_state))
        elif route.startswith("/product/"):
            product_id = int(route.split("/product/")[1])
            page.views.append(build_product_detail_view(page, app_state, product_id))
        elif route == "/cart":
            page.views.append(build_cart_view(page, app_state))
        elif route == "/checkout":
            page.views.append(build_checkout_view(page, app_state))
        elif route.startswith("/order-confirmation/"):
            order_id = int(route.split("/order-confirmation/")[1])
            page.views.append(build_order_confirmation_view(page, app_state, order_id))
        elif route == "/seller":
            if app_state.current_user.role != "seller":
                page.go("/")
                return
            page.views.append(build_seller_dashboard_view(page, app_state))
        else:
            page.go("/")
            return

        page.update()

    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route or "/login")


if __name__ == "__main__":
    init_db(seed=True)

    if os.environ.get("FLET_WEB", "false").lower() == "true":
        # Container / Azure App Service path: bind to 0.0.0.0 and the
        # platform-assigned port so the reverse proxy can reach it.
        port = int(os.environ.get("PORT", 8000))
        ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=port,
               assets_dir="assets")
    else:
        # Local desktop dev run.
        ft.app(target=main, assets_dir="assets")
