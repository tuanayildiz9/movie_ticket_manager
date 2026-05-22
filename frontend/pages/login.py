from nicegui import app, ui

import frontend.services as svc
from frontend.auth import is_logged_in
from frontend.components import navbar


@ui.page("/login")
def login_page() -> None:
    if is_logged_in():
        ui.navigate.to("/")
        return

    navbar()

    with ui.column().classes("w-full items-center justify-center pt-20 min-h-screen bg-gray-950"):
        with ui.card().classes("w-full max-w-sm bg-gray-800 rounded-2xl p-8 shadow-2xl"):
            ui.label("Anmelden").classes("text-2xl font-bold text-amber-400 mb-6 block w-full text-center")

            email_in = (
                ui.input("E-Mail", placeholder="user@example.com")
                .classes("w-full")
                .props("outlined dark color=amber type=email")
            )
            pwd_in = (
                ui.input("Passwort", password=True, password_toggle_button=True)
                .classes("w-full mt-3")
                .props("outlined dark color=amber")
            )
            err = ui.label("").classes("text-red-400 text-sm mt-1 min-h-5")

            def do_login() -> None:
                err.set_text("")
                try:
                    account = svc.user_service().authenticate(email_in.value.strip(), pwd_in.value)
                    if account is None:
                        err.set_text("E-Mail oder Passwort falsch.")
                        return

                    kunde_id_str = ""
                    if account.rolle != "admin":
                        kunde = svc.user_service().get_profile_by_account_id(account.account_id)
                        if kunde:
                            kunde_id_str = str(kunde.kunde_id)

                    app.storage.user.update(
                        {
                            "logged_in": True,
                            "account_id": str(account.account_id),
                            "is_admin": account.rolle == "admin",
                            "email": account.email,
                            "kunde_id": kunde_id_str,
                        }
                    )
                    ui.navigate.to("/")
                except Exception as e:
                    err.set_text(str(e))

            pwd_in.on("keydown.enter", do_login)
            ui.button("Anmelden", on_click=do_login).classes("w-full mt-4").props("unelevated color=amber")

            ui.separator().classes("my-4")
            with ui.row().classes("justify-center gap-1 w-full"):
                ui.label("Noch kein Konto?").classes("text-gray-400 text-sm")
                ui.link("Registrieren", "/register").classes("text-amber-400 text-sm")
