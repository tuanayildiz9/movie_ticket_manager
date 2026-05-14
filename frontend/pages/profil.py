from datetime import date

from nicegui import ui

import frontend.services as svc
from frontend.auth import get_kunde_id, is_logged_in
from frontend.components import navbar


@ui.page("/profil")
def profil_page() -> None:
    if not is_logged_in():
        ui.navigate.to("/login")
        return

    kunde_id = get_kunde_id()
    if not kunde_id:
        ui.notify("Kein Kundenprofil vorhanden.", color="warning")
        ui.navigate.to("/")
        return

    navbar()

    kunde = svc.user_service().get_profile(kunde_id)
    if kunde is None:
        ui.navigate.to("/")
        return

    bestellungen = svc.bestellung_repo().list_by_kunde(kunde_id)
    all_snacks = {s.snack_id: s for s in svc.snack_repo().list_all()}

    with ui.column().classes("w-full max-w-4xl mx-auto px-4 py-8"):
        ui.label("Mein Profil").classes("text-3xl font-bold text-white mb-6")

        # Profile info card
        with ui.card().classes("bg-gray-800 rounded-2xl p-6 mb-6"):
            with ui.row().classes("items-center justify-between mb-4"):
                ui.label("Persönliche Daten").classes("text-xl font-bold text-white")
                _edit_profile_dialog(kunde, kunde_id)

            with ui.grid(columns=2).classes("w-full gap-4"):
                account = svc.user_service().account_repo.get_by_id(kunde.account_id) if kunde.account_id else None
                for label, value in [
                    ("Name", kunde.full_name()),
                    ("E-Mail", account.email if account else "–"),
                    ("Adresse", f"{kunde.adresse}, {kunde.plz}" if kunde.adresse else "–"),
                    ("Telefon", kunde.telefonnummer or "–"),
                    ("Geburtsdatum", str(kunde.geburtsdatum) if kunde.geburtsdatum else "–"),
                    ("Alter", f"{kunde.age()} Jahre" if kunde.geburtsdatum else "–"),
                    ("Zahlungsart", kunde.zahlungsart.name if kunde.zahlungsart else "–"),
                ]:
                    with ui.column().classes("gap-0"):
                        ui.label(label).classes("text-gray-400 text-xs uppercase")
                        ui.label(str(value)).classes("text-white")

        # Saved films
        if kunde.gespeicherte_filme:
            with ui.card().classes("bg-gray-800 rounded-2xl p-6 mb-6"):
                ui.label("Gespeicherte Filme").classes("text-xl font-bold text-white mb-4")
                with ui.row().classes("flex-wrap gap-3"):
                    for film_id in kunde.gespeicherte_filme:
                        film = svc.film_service().get_film_details(film_id)
                        if film:
                            fid_str = str(film_id)
                            ui.button(
                                film.titel,
                                icon="movie",
                                on_click=lambda fid=fid_str: ui.navigate.to(f"/film/{fid}"),
                            ).props("outline color=amber")

        # Order history
        with ui.card().classes("bg-gray-800 rounded-2xl p-6"):
            ui.label("Bestellungen").classes("text-xl font-bold text-white mb-4")
            if not bestellungen:
                ui.label("Noch keine Bestellungen.").classes("text-gray-500")
            else:
                for best in sorted(bestellungen, key=lambda b: b.bestellungsdatum or "", reverse=True):
                    with ui.expansion(
                        f"Bestellung {str(best.bestellung_id)[:8].upper()} – "
                        f"CHF {best.total_betrag:.2f} – "
                        f"{str(best.bestellungsdatum)[:10] if best.bestellungsdatum else '–'}"
                    ).classes("bg-gray-700 rounded-xl mb-2 text-white"):
                        for ticket in best.tickets:
                            film = svc.film_service().get_film_details(ticket.film_id)
                            with ui.card().classes("bg-gray-600 rounded-lg p-3 mb-2"):
                                ui.label(film.titel if film else "Film").classes("text-white font-semibold")
                                ui.label(
                                    f"{ticket.verguenstigungsart.value.capitalize()} · CHF {ticket.preis:.2f}"
                                ).classes("text-gray-300 text-sm")
                                if ticket.snacks:
                                    snack_parts = []
                                    for ts in ticket.snacks:
                                        s = all_snacks.get(ts.snack_id)
                                        if s:
                                            snack_parts.append(f"{s.name} ×{ts.anzahl}")
                                    if snack_parts:
                                        ui.label("Snacks: " + ", ".join(snack_parts)).classes(
                                            "text-gray-400 text-xs"
                                        )


def _edit_profile_dialog(kunde, kunde_id) -> None:
    with ui.dialog() as dialog, ui.card().classes("bg-gray-800 min-w-96"):
        ui.label("Profil bearbeiten").classes("text-xl font-bold text-amber-400 mb-4")

        vorname_in = ui.input("Vorname", value=kunde.vorname or "").classes("w-full").props("outlined dark color=amber")
        nachname_in = (
            ui.input("Nachname", value=kunde.nachname or "").classes("w-full mt-3").props("outlined dark color=amber")
        )
        adresse_in = (
            ui.input("Adresse", value=kunde.adresse or "").classes("w-full mt-3").props("outlined dark color=amber")
        )
        plz_in = ui.input("PLZ", value=kunde.plz or "").classes("w-full mt-3").props("outlined dark color=amber")
        tel_in = (
            ui.input("Telefonnummer", value=kunde.telefonnummer or "")
            .classes("w-full mt-3")
            .props("outlined dark color=amber")
        )

        err = ui.label("").classes("text-red-400 text-sm mt-2")

        def save() -> None:
            try:
                svc.user_service().update_profile(
                    kunde_id,
                    {
                        "vorname": vorname_in.value.strip(),
                        "nachname": nachname_in.value.strip(),
                        "adresse": adresse_in.value.strip(),
                        "plz": plz_in.value.strip(),
                        "telefonnummer": tel_in.value.strip(),
                    },
                )
                ui.notify("Profil gespeichert!", color="positive")
                dialog.close()
                ui.navigate.to("/profil")
            except Exception as e:
                err.set_text(str(e))

        with ui.row().classes("justify-end gap-2 mt-4"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat color=gray")
            ui.button("Speichern", on_click=save).props("unelevated color=amber")

    ui.button("Bearbeiten", icon="edit", on_click=dialog.open).props("outline color=amber")
