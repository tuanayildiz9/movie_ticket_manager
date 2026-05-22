from datetime import date, datetime

from nicegui import ui

import frontend.services as svc
from frontend.auth import is_logged_in
from frontend.components import navbar


@ui.page("/register")
def register_page() -> None:
    if is_logged_in():
        ui.navigate.to("/")
        return

    navbar()

    zahlungsarten = svc.get_all_zahlungsarten()
    zahlung_options = {z["name"]: z["name"] for z in zahlungsarten}

    with ui.column().classes("w-full items-center py-12 min-h-screen bg-gray-950"):
        with ui.card().classes("w-full max-w-lg bg-gray-800 rounded-2xl p-8 shadow-2xl"):
            ui.label("Konto erstellen").classes("text-2xl font-bold text-amber-400 mb-6")

            with ui.grid(columns=2).classes("w-full gap-3"):
                vorname_in = ui.input("Vorname").props("outlined dark color=amber")
                nachname_in = ui.input("Nachname").props("outlined dark color=amber")

            email_in = (
                ui.input("E-Mail", placeholder="user@example.com")
                .classes("w-full mt-3")
                .props("outlined dark color=amber type=email")
            )
            pwd_in = (
                ui.input("Passwort", password=True, password_toggle_button=True)
                .classes("w-full mt-3")
                .props("outlined dark color=amber")
            )
            adresse_in = ui.input("Adresse").classes("w-full mt-3").props("outlined dark color=amber")

            with ui.row().classes("w-full gap-3 mt-3"):
                plz_in = ui.input("PLZ").props("outlined dark color=amber").classes("w-28")
                ort_in = ui.input("Ort").props("outlined dark color=amber").classes("flex-1")
            tel_in = ui.input("Telefonnummer").classes("w-full mt-3").props("outlined dark color=amber")

            geb_in = (
                ui.input("Geburtsdatum (TT.MM.JJJJ)", placeholder="z. B. 15.06.1995")
                .classes("w-full mt-3")
                .props("outlined dark color=amber")
            )

            zahlung_sel = (
                ui.select(
                    label="Zahlungsart",
                    options=zahlung_options,
                    value=zahlungsarten[0]["name"] if zahlungsarten else None,
                )
                .classes("w-full mt-3")
                .props("outlined dark color=amber")
            )

            err = ui.label("").classes("text-red-400 text-sm mt-2 min-h-5")

            def do_register() -> None:
                err.set_text("")
                try:
                    raw_date = (geb_in.value or "").strip()
                    if not raw_date:
                        err.set_text("Bitte Geburtsdatum eingeben.")
                        return
                    try:
                        geb_date = datetime.strptime(raw_date, "%d.%m.%Y").date()
                    except ValueError:
                        err.set_text("Datum ungültig – bitte Format TT.MM.JJJJ verwenden (z. B. 15.06.1995).")
                        return
                    data = {
                        "email": email_in.value.strip(),
                        "passwort": pwd_in.value,
                        "vorname": vorname_in.value.strip(),
                        "nachname": nachname_in.value.strip(),
                        "adresse": adresse_in.value.strip(),
                        "plz": plz_in.value.strip(),
                        "ort": ort_in.value.strip(),
                        "geburtsdatum": geb_date,
                        "telefonnummer": tel_in.value.strip(),
                        "zahlungsart": zahlung_sel.value,
                    }
                    svc.user_service().register(data)
                    ui.notify("Konto erfolgreich erstellt!", color="positive")
                    ui.navigate.to("/login")
                except ValueError as e:
                    err.set_text(str(e))
                except Exception as e:
                    err.set_text(f"Fehler: {e}")

            ui.button("Konto erstellen", on_click=do_register).classes("w-full mt-6").props("unelevated color=amber")

            ui.separator().classes("my-4")
            with ui.row().classes("justify-center gap-1 w-full"):
                ui.label("Bereits ein Konto?").classes("text-gray-400 text-sm")
                ui.link("Anmelden", "/login").classes("text-amber-400 text-sm")
