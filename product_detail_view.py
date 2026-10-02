import flet as ft
from services import catalog_service


def build_product_detail_view(page: ft.Page, app_state, product_id: int) -> ft.View:
    product = catalog_service.get_product(product_id)
    qty_text = ft.Text("1", size=14, weight=ft.FontWeight.BOLD)
    quantity = {"value": 1}
    snackbar = ft.SnackBar(content=ft.Text(""))
    page.overlay.append(snackbar)

    def change_qty(delta):
        new_val = max(1, min(product.stock_qty, quantity["value"] + delta))
        quantity["value"] = new_val
        qty_text.value = str(new_val)
        page.update()

    def add_to_cart(e):
        app_state.cart.add_item(product.id, quantity["value"])
        snackbar.content = ft.Text(f"Added {quantity['value']} x {product.name} to cart.")
        snackbar.open = True
        page.update()

    stock_note = (
        ft.Text(f"In stock ({product.stock_qty} available)", color="#2A7A2A", size=12)
        if product.stock_qty > 0 else
        ft.Text("Out of stock", color="#C0392B", size=12)
    )

    return ft.View(
        route=f"/product/{product_id}",
        controls=[
            ft.Row([
                ft.TextButton("← Back", on_click=lambda e: page.go("/")),
                ft.IconButton(icon=ft.Icons.SHOPPING_CART_OUTLINED,
                              on_click=lambda e: page.go("/cart")),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(width=280, height=280, bgcolor="#EEEEEE",
                                 border=ft.border.all(1, "#BBBBBB"),
                                 alignment=ft.alignment.center,
                                 content=ft.Icon(ft.Icons.IMAGE_OUTLINED, size=48, color="#999999")),
                    ft.Column(
                        expand=True,
                        controls=[
                            ft.Text(product.name, size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(f"${product.price:.2f}", size=18, color="#1F4E78",
                                    weight=ft.FontWeight.BOLD),
                            stock_note,
                            ft.Text("Description", size=12, color=ft.Colors.GREY),
                            ft.Container(
                                padding=10, bgcolor="#FAFAFA",
                                border=ft.border.all(1, "#E0E0E0"),
                                content=ft.Text(product.description or "No description provided."),
                            ),
                            ft.Text("Quantity", size=12, color=ft.Colors.GREY),
                            ft.Row([
                                ft.IconButton(icon=ft.Icons.REMOVE, on_click=lambda e: change_qty(-1)),
                                qty_text,
                                ft.IconButton(icon=ft.Icons.ADD, on_click=lambda e: change_qty(1)),
                            ]),
                            ft.ElevatedButton(
                                "Add to Cart", bgcolor="#1F4E78", color="white",
                                disabled=product.stock_qty == 0,
                                on_click=add_to_cart,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
