import flet as ft
from services import catalog_service


def build_home_view(page: ft.Page, app_state) -> ft.View:
    search_field = ft.TextField(
        hint_text="Search shoes...", width=320, height=40,
        border_radius=6, content_padding=10,
    )
    grid = ft.GridView(expand=True, runs_count=3, max_extent=220,
                        child_aspect_ratio=0.8, spacing=12, run_spacing=12)

    def product_card(product):
        return ft.Container(
            padding=10, border_radius=6, bgcolor="#FAFAFA",
            border=ft.border.all(1, "#CCCCCC"),
            content=ft.Column(
                controls=[
                    ft.Container(height=90, bgcolor="#EEEEEE",
                                 border=ft.border.all(1, "#BBBBBB"),
                                 alignment=ft.alignment.center,
                                 content=ft.Icon(ft.Icons.IMAGE_OUTLINED, color="#999999")),
                    ft.Text(product.name, size=13, weight=ft.FontWeight.W_500),
                    ft.Text(f"${product.price:.2f}", size=13, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.ElevatedButton(
                            "View", bgcolor="#1F4E78", color="white",
                            on_click=lambda e, pid=product.id: page.go(f"/product/{pid}"),
                        )
                    ]),
                ],
            ),
            on_click=lambda e, pid=product.id: page.go(f"/product/{pid}"),
        )

    def refresh(search=""):
        grid.controls = [product_card(p) for p in catalog_service.list_products(search)]

    def on_search_change(e):
        refresh(search_field.value)
        page.update()

    search_field.on_change = on_search_change
    refresh()

    def cart_count():
        return sum(i.quantity for i in app_state.cart.get_items())

    return ft.View(
        route="/",
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Image(src="logo.png", height=40),
                    search_field,
                    ft.IconButton(
                        icon=ft.Icons.SHOPPING_CART_OUTLINED,
                        tooltip=f"Cart ({cart_count()} item(s))",
                        on_click=lambda e: page.go("/cart"),
                    ),
                ],
            ),
            ft.Divider(),
            grid,
        ],
    )
