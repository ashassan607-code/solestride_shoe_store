import flet as ft
from services import auth_service


def build_login_view(page: ft.Page, app_state) -> ft.View:
    email_field = ft.TextField(label="Email", width=320, value="buyer@example.com")
    password_field = ft.TextField(label="Password", width=320, password=True,
                                   can_reveal_password=True, value="password123")
    error_text = ft.Text("", color=ft.Colors.RED)

    def do_login(e):
        try:
            user = auth_service.login(email_field.value.strip(), password_field.value)
            app_state.current_user = user
            page.go("/seller" if user.role == "seller" else "/")
        except ValueError as ex:
            error_text.value = str(ex)
            page.update()

    def go_register(e):
        page.go("/register")

    return ft.View(
        route="/login",
        controls=[
            ft.Container(
                alignment=ft.alignment.center,
                expand=True,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Image(src="logo.png", height=56),
                        ft.Text("Sign in", size=16, color=ft.Colors.GREY_700),
                        email_field,
                        password_field,
                        error_text,
                        ft.ElevatedButton("Log In", on_click=do_login, width=320,
                                          bgcolor="#1F4E78", color="white"),
                        ft.TextButton("Don't have an account? Register", on_click=go_register),
                        ft.Text("Demo accounts: seller@example.com / buyer@example.com, "
                                "password: password123", size=11, color=ft.Colors.GREY),
                    ],
                ),
            )
        ],
    )


def build_register_view(page: ft.Page, app_state) -> ft.View:
    name_field = ft.TextField(label="Full Name", width=320)
    email_field = ft.TextField(label="Email", width=320)
    password_field = ft.TextField(label="Password", width=320, password=True,
                                   can_reveal_password=True)
    role_dropdown = ft.Dropdown(
        label="Account type", width=320,
        options=[ft.dropdown.Option("buyer"), ft.dropdown.Option("seller")],
        value="buyer",
    )
    error_text = ft.Text("", color=ft.Colors.RED)

    def do_register(e):
        try:
            user = auth_service.register(
                name_field.value.strip(), email_field.value.strip(),
                password_field.value, role_dropdown.value,
            )
            app_state.current_user = user
            page.go("/seller" if user.role == "seller" else "/")
        except ValueError as ex:
            error_text.value = str(ex)
            page.update()

    return ft.View(
        route="/register",
        controls=[
            ft.Container(
                alignment=ft.alignment.center,
                expand=True,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Image(src="logo.png", height=48),
                        ft.Text("Create account", size=22, weight=ft.FontWeight.BOLD),
                        name_field, email_field, password_field, role_dropdown,
                        error_text,
                        ft.ElevatedButton("Register", on_click=do_register, width=320,
                                          bgcolor="#1F4E78", color="white"),
                        ft.TextButton("Back to login", on_click=lambda e: page.go("/login")),
                    ],
                ),
            )
        ],
    )
