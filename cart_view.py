import flet as ft
from services import order_service


def build_cart_view(page: ft.Page, app_state) -> ft.View:
    cart = app_state.cart
    lines_column = ft.Column(spacing=10)

    def refresh():
        lines_column.controls.clear()
        for entry in cart.get_items_with_products():
            item, product = entry["item"], entry["product"]

            def make_handlers(pid=product.id):
                def inc(e):
                    cart.update_quantity(pid, cart._items[pid].quantity + 1)
                    refresh(); page.update()
                def dec(e):
                    cart.update_quantity(pid, cart._items[pid].quantity - 1)
                    refresh(); page.update()
                def remove(e):
                    cart.remove_item(pid)
                    refresh(); page.update()
                return inc, dec, remove

            inc, dec, remove = make_handlers()
            lines_column.controls.append(
                ft.Container(
                    padding=10, bgcolor="#FAFAFA", border=ft.border.all(1, "#E0E0E0"),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row([
                                ft.Container(width=50, height=50, bgcolor="#EEEEEE",
                                             border=ft.border.all(1, "#BBBBBB")),
                                ft.Column([
                                    ft.Text(product.name, size=13),
                                    ft.Text(f"${product.price:.2f}", size=12, color=ft.Colors.GREY),
                                    ft.Row([
                                        ft.IconButton(icon=ft.Icons.REMOVE, icon_size=16, on_click=dec),
                                        ft.Text(str(item.quantity)),
                                        ft.IconButton(icon=ft.Icons.ADD, icon_size=16, on_click=inc),
                                    ]),
                                ]),
                            ]),
                            ft.TextButton("Remove", style=ft.ButtonStyle(color="#C0392B"),
                                          on_click=remove),
                        ],
                    ),
                )
            )
        subtotal_text.value = f"${cart.subtotal():.2f}"
        total_text.value = f"${cart.subtotal() + order_service.DELIVERY_FEE:.2f}"
        checkout_btn.disabled = len(cart.get_items()) == 0

    subtotal_text = ft.Text("$0.00")
    total_text = ft.Text("$0.00", weight=ft.FontWeight.BOLD)
    checkout_btn = ft.ElevatedButton(
        "Checkout", bgcolor="#1F4E78", color="white",
        on_click=lambda e: page.go("/checkout"),
    )

    summary = ft.Container(
        width=220, padding=16, bgcolor="#F5F7FA", border=ft.border.all(1, "#C9D4E0"),
        content=ft.Column([
            ft.Text("Order Summary", weight=ft.FontWeight.BOLD),
            ft.Row([ft.Text("Subtotal"), subtotal_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([ft.Text("Delivery"), ft.Text(f"${order_service.DELIVERY_FEE:.2f}")],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            ft.Row([ft.Text("Total", weight=ft.FontWeight.BOLD), total_text],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            checkout_btn,
        ]),
    )

    refresh()

    return ft.View(
        route="/cart",
        controls=[
            ft.Row([
                ft.Text("Your Cart", size=22, weight=ft.FontWeight.BOLD),
                ft.TextButton("Continue shopping", on_click=lambda e: page.go("/")),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Column([lines_column], expand=True) if cart.get_items()
                    else ft.Text("Your cart is empty.", color=ft.Colors.GREY),
                    summary,
                ],
            ),
        ],
    )
