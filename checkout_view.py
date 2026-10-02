import flet as ft
from services import order_service


def build_checkout_view(page: ft.Page, app_state) -> ft.View:
    cart = app_state.cart
    name_field = ft.TextField(label="Full Name", width=400)
    phone_field = ft.TextField(label="Phone Number", width=400)
    address_field = ft.TextField(label="Delivery Address", width=400, multiline=True, min_lines=2)
    payment_method = ft.RadioGroup(
        value="transfer",
        content=ft.Row([
            ft.Radio(value="transfer", label="Card / Transfer"),
            ft.Radio(value="cod", label="Pay on Delivery"),
        ]),
    )
    error_text = ft.Text("", color=ft.Colors.RED)

    def place_order(e):
        if not name_field.value or not phone_field.value or not address_field.value:
            error_text.value = "Please fill in all shipping details."
            page.update()
            return
        try:
            order = order_service.checkout(app_state.current_user.id, cart)
            page.go(f"/order-confirmation/{order.id}")
        except ValueError as ex:
            error_text.value = str(ex)
            page.update()

    summary = ft.Container(
        width=220, padding=16, bgcolor="#F5F7FA", border=ft.border.all(1, "#C9D4E0"),
        content=ft.Column([
            ft.Text("Order Summary", weight=ft.FontWeight.BOLD),
            ft.Text(f"{len(cart.get_items())} item(s)", size=12, color=ft.Colors.GREY),
            ft.Divider(),
            ft.Row([
                ft.Text("Total", weight=ft.FontWeight.BOLD),
                ft.Text(f"${cart.subtotal() + order_service.DELIVERY_FEE:.2f}",
                        weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ]),
    )

    return ft.View(
        route="/checkout",
        controls=[
            ft.Text("Checkout", size=22, weight=ft.FontWeight.BOLD),
            ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Column([
                        name_field, phone_field, address_field,
                        ft.Text("Payment Method", size=12, color=ft.Colors.GREY),
                        payment_method,
                        error_text,
                        ft.ElevatedButton("Place Order", bgcolor="#1F4E78", color="white",
                                          width=400, on_click=place_order),
                    ]),
                    summary,
                ],
            ),
        ],
    )


def build_order_confirmation_view(page: ft.Page, app_state, order_id: int) -> ft.View:
    return ft.View(
        route=f"/order-confirmation/{order_id}",
        controls=[
            ft.Container(
                expand=True, alignment=ft.alignment.center,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color="#2A7A2A", size=48),
                        ft.Text("Order placed!", size=22, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Your order ID is #{order_id}."),
                        ft.ElevatedButton("Continue shopping",
                                          on_click=lambda e: page.go("/")),
                    ],
                ),
            )
        ],
    )
