from uuid import UUID

from nicegui import ui

import frontend.services as svc
from frontend.auth import get_kunde_id, is_admin, is_logged_in
from frontend.components import film_cover, navbar


_GERMAN_MONTHS = [
    "Januar",
    "Februar",
    "März",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Dezember",
]


def _format_german_date(value) -> str:
    if value is None:
        return "–"
    return f"{value.day:02d}. {_GERMAN_MONTHS[value.month - 1]} {value.year}"


@ui.page("/film/{film_id}")
def film_detail_page(film_id: str) -> None:
    if not is_logged_in():
        ui.navigate.to("/login")
        return

    navbar()

    try:
        fid = UUID(film_id)
    except ValueError:
        ui.navigate.to("/")
        return

    film = svc.film_service().get_film_details(fid)
    if film is None:
        with ui.column().classes("w-full items-center py-20"):
            ui.label("Film nicht gefunden.").classes("text-gray-400 text-xl")
            ui.button("Zurück", on_click=lambda: ui.navigate.to("/")).props("flat color=amber")
        return

    avg_rating = svc.film_service().get_average_rating(fid)
    kat_names = svc.get_kategorie_names(film.kategorie_ids)
    spr_names = svc.get_sprache_names(film.sprache_ids)
    bewertungen = svc.film_service().bewertung_repo.list_by_film(fid)

    with ui.column().classes("w-full max-w-5xl mx-auto px-4 py-8"):
        # Back link
        ui.link("← Zurück zu Filmen", "/").classes("text-amber-400 text-sm mb-6 block")

        # Film header
        with ui.row().classes("w-full gap-8 flex-wrap"):
            # Cover
            with ui.element("div").classes("w-56 flex-shrink-0"):
                film_cover(film.coverbild_url, "h-80")

            # Info
            with ui.column().classes("flex-1 gap-3 min-w-0"):
                ui.label(film.titel).classes("text-3xl font-bold text-white")
                with ui.row().classes("items-center gap-2 flex-wrap"):
                    ui.badge(f"FSK {film.altersfreigabe}").props("color=amber")
                    for k in kat_names:
                        ui.badge(k).props("color=blue-grey")
                    for s in spr_names:
                        ui.badge(s).props("color=teal outline")

                if film.hauptdarsteller:
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("person").classes("text-gray-400 text-base")
                        ui.label(film.hauptdarsteller).classes("text-gray-300 text-sm")

                if film.erscheinungsdatum:
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("calendar_today").classes("text-gray-400 text-base")
                        ui.label(_format_german_date(film.erscheinungsdatum)).classes("text-gray-300 text-sm")

                ui.label(f"Basispreis: CHF {film.basispreis:.2f}").classes("text-amber-400 text-lg font-semibold")

                # Star rating
                with ui.row().classes("items-center gap-2"):
                    stars = "★" * round(float(avg_rating)) + "☆" * (5 - round(float(avg_rating)))
                    ui.label(stars).classes("text-amber-400 text-xl")
                    ui.label(f"{avg_rating:.1f} / 5.0 ({len(bewertungen)} Bewertungen)").classes("text-gray-400 text-sm")

                if film.beschreibung:
                    ui.label(film.beschreibung).classes("text-gray-300 text-sm leading-relaxed mt-2")

        ui.separator().classes("my-8 border-gray-700")

        # Screenings
        ui.label("Vorstellungen").classes("text-xl font-bold text-white mb-4")
        if not film.vorstellungen:
            ui.label("Keine Vorstellungen verfügbar.").classes("text-gray-500")
        else:
            for vorstellung in film.vorstellungen:
                freie = vorstellung.free_seat_count()
                with ui.card().classes("bg-gray-800 rounded-xl p-4 mb-3"):
                    with ui.row().classes("items-center justify-between flex-wrap gap-3"):
                        with ui.column().classes("gap-1"):
                            with ui.row().classes("items-center gap-2"):
                                ui.icon("event").classes("text-amber-400")
                                ui.label(
                                    vorstellung.startzeit.strftime("%d.%m.%Y %H:%M")
                                    if vorstellung.startzeit
                                    else "–"
                                ).classes("text-white font-semibold")
                            with ui.row().classes("items-center gap-4 text-sm text-gray-400"):
                                with ui.row().classes("items-center gap-1"):
                                    ui.icon("place", size="sm")
                                    ui.label(f"{vorstellung.ort}, {vorstellung.saal}")
                                with ui.row().classes("items-center gap-1"):
                                    ui.icon("event_seat", size="sm")
                                    ui.label(f"{freie} freie Plätze")

                        vid_str = str(vorstellung.vorstellung_id)
                        fid_str = str(film.film_id)
                        # Button ausgrauen, wenn Vorstellung in der Vergangenheit liegt
                        is_past_v = False
                        if getattr(vorstellung, "startzeit", None) is not None:
                            from datetime import datetime

                            is_past_v = vorstellung.startzeit < datetime.utcnow()

                        if freie > 0 and not is_admin():
                            if is_past_v:
                                # deutliche Kennzeichnung: Button ausgegraut + erklärender Hinweis
                                with ui.row().classes("items-center gap-3"):
                                    ui.button("Ticket buchen", icon="confirmation_number").props("unelevated color=amber disable")
                                    ui.badge("Vergangen").props("color=gray")
                                    ui.label("Diese Vorstellung liegt in der Vergangenheit; Buchung nicht möglich.").classes("text-gray-400 text-sm")
                            else:
                                ui.button(
                                    "Ticket buchen",
                                    icon="confirmation_number",
                                    on_click=lambda v=vid_str, f=fid_str: ui.navigate.to(
                                        f"/checkout/{v}?film_id={f}"
                                    ),
                                ).props("unelevated color=amber")
                        elif freie == 0:
                            ui.badge("Ausverkauft").props("color=red")

        ui.separator().classes("my-8 border-gray-700")

        # Ratings section
        with ui.row().classes("items-center justify-between mb-4"):
            ui.label("Bewertungen").classes("text-xl font-bold text-white")
            if not is_admin() and get_kunde_id():
                _rating_dialog(film_id)

        if not bewertungen:
            ui.label("Noch keine Bewertungen.").classes("text-gray-500")
        else:
            for bew in bewertungen:
                with ui.card().classes("bg-gray-800 rounded-xl p-4 mb-3"):
                    stars = "★" * bew.bewertung + "☆" * (5 - bew.bewertung)
                    with ui.row().classes("items-center justify-between"):
                        ui.label(stars).classes("text-amber-400 text-lg")
                        if bew.bewertungsdatum:
                            ui.label(str(bew.bewertungsdatum)[:10]).classes("text-gray-500 text-sm")
                    if bew.kommentar:
                        ui.label(bew.kommentar).classes("text-gray-300 text-sm mt-2")


def _rating_dialog(film_id: str) -> None:
    with ui.dialog() as dialog, ui.card().classes("bg-gray-800 min-w-80"):
        ui.label("Bewertung abgeben").classes("text-xl font-bold text-amber-400 mb-4")
        score_sel = (
            ui.select(options={1: "1 ★", 2: "2 ★★", 3: "3 ★★★", 4: "4 ★★★★", 5: "5 ★★★★★"}, value=5, label="Bewertung")
            .classes("w-full")
            .props("outlined dark color=amber")
        )
        comment_in = (
            ui.textarea("Kommentar (optional)").classes("w-full mt-3").props("outlined dark color=amber rows=3")
        )
        err = ui.label("").classes("text-red-400 text-sm mt-1")

        def submit() -> None:
            kunde_id = get_kunde_id()
            if not kunde_id:
                err.set_text("Kein Kundenkonto gefunden.")
                return
            try:
                svc.film_service().rate_film(kunde_id, UUID(film_id), score_sel.value, comment_in.value)
                ui.notify("Bewertung gespeichert!", color="positive")
                dialog.close()
                ui.navigate.to(f"/film/{film_id}")
            except Exception as e:
                err.set_text(str(e))

        with ui.row().classes("justify-end gap-2 mt-4"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat color=gray")
            ui.button("Absenden", on_click=submit).props("unelevated color=amber")

    ui.button("Bewertung schreiben", icon="star", on_click=dialog.open).props("outline color=amber")
