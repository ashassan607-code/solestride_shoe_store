import flet as ft
from services import catalog_service, order_service


def build_seller_dashboard_view(page: ft.Page, app_state) -> ft.View:
    seller = app_state.current_user
    content_area = ft.Column(expand=True)

    def show_products(e=None):
        products = catalog_service.list_seller_products(seller.id)
        rows = []
        for p in products:
            low = catalog_service.is_low_stock(p)
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(p.name)),
                ft.DataCell(ft.Text(f"${p.price:.2f}")),
                ft.DataCell(ft.Text(f"{p.stock_qty}" + (" (low)" if low else ""),
                                     color="#C0392B" if low else None)),
                ft.DataCell(ft.Row([
                    ft.TextButton("Edit", on_click=lambda e, pid=p.id: open_product_form(pid)),
                    ft.TextButton("Delete", style=ft.ButtonStyle(color="#C0392B"),
                                  on_click=lambda e, pid=p.id: delete_product(pid)),
                ])),
            ]))
        content_area.controls = [
            ft.Row([
                ft.Text("Products", size=18, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("+ Add Shoe", bgcolor="#1F4E78", color="white",
                                  on_click=lambda e: open_product_form(None)),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.DataTable(
                columns=[ft.DataColumn(ft.Text(c)) for c in ["Product", "Price", "Stock", "Actions"]],
                rows=rows,
            ) if rows else ft.Text("No products yet.", color=ft.Colors.GREY),
        ]
        page.update()

    def delete_product(product_id):
        catalog_service.delete_product(product_id)
        show_products()

    def open_product_form(product_id):
        existing = catalog_service.get_product(product_id) if product_id else None
        name_f = ft.TextField(label="Name", value=existing.name if existing else "", width=350)
        desc_f = ft.TextField(label="Description", value=existing.description if existing else "",
                               width=350, multiline=True)
        price_f = ft.TextField(label="Price", value=str(existing.price) if existing else "",
                                width=170)
        stock_f = ft.TextField(label="Stock", value=str(existing.stock_qty) if existing else "",
                                width=170)
        err = ft.Text("", color=ft.Colors.RED)

        def save(e):
            try:
                catalog_service.upsert_product(
                    seller_id=seller.id, product_id=product_id,
                    name=name_f.value, description=desc_f.value,
                    price=float(price_f.value), stock_qty=int(stock_f.value),
                )
                close_dialog()
                show_products()
            except (ValueError, TypeError):
                err.value = "Enter a valid price and stock quantity."
                page.update()

        def close_dialog():
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Shoe" if existing else "Add Shoe"),
            content=ft.Column([name_f, desc_f, ft.Row([price_f, stock_f]), err],
                               tight=True, height=260),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: close_dialog()),
                ft.ElevatedButton("Save", on_click=save),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def show_orders(e=None):
        orders = order_service.list_seller_orders(seller.id)
        rows = []
        for o in orders:
            next_action = None
            if o["status"] == "pending":
                next_action = ("Mark Shipped", "shipped")
            elif o["status"] == "shipped":
                next_action = ("Mark Delivered", "delivered")

            def make_advance(order_id=o["id"], current=o["status"], target=next_action[1] if next_action else None):
                def handler(e):
                    order_service.advance_status(order_id, current, target)
                    show_orders()
                return handler

            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(f"#{o['id']}")),
                ft.DataCell(ft.Text(f"${o['total']:.2f}")),
                ft.DataCell(ft.Text(o["status"].capitalize())),
                ft.DataCell(
                    ft.TextButton(next_action[0], on_click=make_advance())
                    if next_action else ft.Text("—", color=ft.Colors.GREY)
                ),
            ]))
        content_area.controls = [
            ft.Text("Orders", size=18, weight=ft.FontWeight.BOLD),
            ft.DataTable(
                columns=[ft.DataColumn(ft.Text(c)) for c in ["Order", "Total", "Status", "Action"]],
                rows=rows,
            ) if rows else ft.Text("No orders yet.", color=ft.Colors.GREY),
        ]
        page.update()

    sidebar = ft.Container(
        width=160, bgcolor="#1F4E78", padding=20,
        content=ft.Column([
            ft.Image(src="logo_icon.png", height=40),
            ft.Container(height=16),
            ft.TextButton("Products", style=ft.ButtonStyle(color="white"), on_click=show_products),
            ft.TextButton("Orders", style=ft.ButtonStyle(color="white"), on_click=show_orders),
            ft.TextButton("Log out", style=ft.ButtonStyle(color="white"),
                          on_click=lambda e: (setattr(app_state, "current_user", None), page.go("/login"))),
        ]),
    )

    show_products()

    return ft.View(
        route="/seller",
        padding=0,
        controls=[
            ft.Row(expand=True, controls=[
                sidebar,
                ft.Container(expand=True, padding=20, content=content_area),
            ]),
        ],
    )
