from decimal import Decimal
from uuid import UUID

from fastapi import Request
from nicegui import ui

import frontend.services as svc
from frontend.auth import get_kunde_id, is_logged_in
from frontend.components import navbar


@ui.page("/checkout/{vorstellung_id}")
def checkout_page(request: Request, vorstellung_id: str) -> None:
    if not is_logged_in():
        ui.navigate.to("/login")
        return

    kunde_id = get_kunde_id()
    if not kunde_id:
        ui.notify("Nur für Kunden verfügbar.", color="negative")
        ui.navigate.to("/")
        return

    film_id_str = request.query_params.get("film_id", "")
    try:
        vid = UUID(vorstellung_id)
        fid = UUID(film_id_str)
    except ValueError:
        ui.navigate.to("/")
        return

    film = svc.film_service().get_film_details(fid)
    vorstellung = next((v for v in (film.vorstellungen if film else []) if v.vorstellung_id == vid), None)
    if film is None or vorstellung is None:
        ui.navigate.to("/")
        return

    available_seats = svc.bestellung_service().available_seats(vid)
    all_snacks = svc.snack_repo().list_all()

    # Checkout state
    selected_seat: dict[str, UUID | None] = {"id": None}
    discount_val: dict[str, str] = {"v": "regulaer"}
    snack_counts: dict[UUID, int] = {s.snack_id: 0 for s in all_snacks}

    navbar()

    with ui.column().classes("w-full max-w-4xl mx-auto px-4 py-8"):
        ui.link(f"← Zurück zu {film.titel}", f"/film/{fid}").classes("text-amber-400 text-sm mb-6 block")
        ui.label("Ticket buchen").classes("text-3xl font-bold text-white mb-2")

        # Screening info
        with ui.card().classes("bg-gray-800 rounded-xl p-4 mb-6"):
            with ui.row().classes("items-center gap-6 flex-wrap"):
                with ui.column().classes("gap-1"):
                    ui.label(film.titel).classes("text-white font-bold text-lg")
                    ui.label(
                        f"{vorstellung.startzeit.strftime('%d.%m.%Y %H:%M') if vorstellung.startzeit else '–'} · "
                        f"{vorstellung.ort}, {vorstellung.saal}"
                    ).classes("text-gray-400 text-sm")
                ui.label(f"CHF {film.basispreis:.2f}").classes("text-amber-400 font-bold text-xl ml-auto")

        with ui.row().classes("w-full gap-6 flex-wrap items-start"):
            # Left column: seat + discount
            with ui.column().classes("flex-1 min-w-72 gap-4"):
                # Seat selection
                ui.label("Sitzplatz wählen").classes("text-lg font-bold text-white")
                seat_display = ui.label("Kein Sitzplatz ausgewählt").classes("text-gray-400 text-sm")

                if not available_seats:
                    ui.label("Keine freien Sitzplätze verfügbar.").classes("text-red-400")
                else:
                    # Group by sector
                    sektoren: dict[str, list] = {}
                    for seat in available_seats:
                        sektoren.setdefault(seat["sektor"], []).append(seat)

                    seat_buttons: dict[str, ui.button] = {}

                    def make_seat_click(seat_info: dict):
                        def on_click():
                            prev = selected_seat["id"]
                            selected_seat["id"] = seat_info["sitzplatz_id"]
                            seat_display.set_text(
                                f"Gewählt: {seat_info['sektor']}{seat_info['sitz_label']} – Sitzplatz"
                            )
                            # Reset previous button style
                            if prev and str(prev) in seat_buttons:
                                seat_buttons[str(prev)].props("outline color=amber")
                            # Highlight selected
                            seat_buttons[str(seat_info["sitzplatz_id"])].props("unelevated color=amber")
                            _update_total()

                        return on_click

                    for sektor, seats in sektoren.items():
                        ui.label(f"Reihe {sektor}").classes("text-gray-400 text-xs font-semibold uppercase mt-2")
                        with ui.row().classes("flex-wrap gap-2"):
                            for seat in seats:
                                sid_str = str(seat["sitzplatz_id"])
                                btn = (
                                    ui.button(seat["sitz_label"], on_click=make_seat_click(seat))
                                    .props("outline color=amber")
                                    .classes("min-w-12")
                                )
                                seat_buttons[sid_str] = btn

                # Discount
                ui.label("Vergünstigung").classes("text-lg font-bold text-white mt-4")
                discount_info = {
                    "regulaer": ("Regulär", "±0 CHF"),
                    "student": ("Student", "−4.00 CHF"),
                    "senior": ("Senior", "−3.00 CHF"),
                    "kind": ("Kind", "−6.00 CHF"),
                }
                discount_sel = (
                    ui.select(
                        options={k: f"{v[0]} ({v[1]})" for k, v in discount_info.items()},
                        value="regulaer",
                        label="Vergünstigung",
                    )
                    .classes("w-full")
                    .props("outlined dark color=amber")
                )

                def on_discount_change(e) -> None:
                    discount_val["v"] = e.value
                    _update_total()

                discount_sel.on_value_change(on_discount_change)

            # Right column: snacks + summary
            with ui.column().classes("w-72 gap-4 flex-shrink-0"):
                # Snacks
                if all_snacks:
                    ui.label("Snacks hinzufügen").classes("text-lg font-bold text-white")
                    with ui.card().classes("bg-gray-800 rounded-xl p-4"):
                        snack_counters: dict[UUID, ui.label] = {}
                        for snack in all_snacks:
                            with ui.row().classes("items-center justify-between w-full"):
                                with ui.column().classes("gap-0"):
                                    ui.label(snack.name).classes("text-white text-sm")
                                    ui.label(f"CHF {snack.preis:.2f}").classes("text-amber-400 text-xs")
                                with ui.row().classes("items-center gap-2"):
                                    cnt_label = ui.label("0").classes("text-white text-sm min-w-5 text-center")
                                    snack_counters[snack.snack_id] = cnt_label

                                    def make_snack_handlers(s_id: UUID, s_lbl: ui.label):
                                        def dec():
                                            if snack_counts[s_id] > 0:
                                                snack_counts[s_id] -= 1
                                                s_lbl.set_text(str(snack_counts[s_id]))
                                                _update_total()

                                        def inc():
                                            snack_counts[s_id] += 1
                                            s_lbl.set_text(str(snack_counts[s_id]))
                                            _update_total()

                                        return dec, inc

                                    dec_fn, inc_fn = make_snack_handlers(snack.snack_id, cnt_label)
                                    ui.button(icon="remove", on_click=dec_fn).props("flat dense color=gray round")
                                    ui.button(icon="add", on_click=inc_fn).props("flat dense color=amber round")

                # Price summary
                ui.label("Preiszusammenfassung").classes("text-lg font-bold text-white mt-2")
                with ui.card().classes("bg-gray-800 rounded-xl p-4"):
                    total_label = ui.label(f"CHF {film.basispreis:.2f}").classes(
                        "text-2xl font-bold text-amber-400"
                    )
                    detail_label = ui.label(
                        f"Ticket: CHF {film.basispreis:.2f}"
                    ).classes("text-gray-400 text-sm")

                def _update_total() -> None:
                    discounts = {"regulaer": 0, "student": -4, "senior": -3, "kind": -6}
                    ticket_price = film.basispreis + Decimal(discounts.get(discount_val["v"], 0))
                    snack_total = sum(
                        s.preis * snack_counts[s.snack_id] for s in all_snacks if snack_counts[s.snack_id] > 0
                    )
                    total = ticket_price + snack_total
                    total_label.set_text(f"CHF {total:.2f}")
                    lines = [f"Ticket: CHF {ticket_price:.2f}"]
                    for s in all_snacks:
                        if snack_counts[s.snack_id] > 0:
                            lines.append(f"{s.name} ×{snack_counts[s.snack_id]}: CHF {s.preis * snack_counts[s.snack_id]:.2f}")
                    detail_label.set_text(" | ".join(lines))

                err_label = ui.label("").classes("text-red-400 text-sm mt-2")

                def place_order() -> None:
                    if selected_seat["id"] is None:
                        err_label.set_text("Bitte einen Sitzplatz auswählen.")
                        return
                    try:
                        ticket_data = [
                            {
                                "film_id": fid,
                                "vorstellung_id": vid,
                                "sitzplatz_id": selected_seat["id"],
                                "verguenstigungsart": discount_val["v"],
                            }
                        ]
                        snack_data = [
                            {"ticket_index": 0, "snack_id": sid, "anzahl": cnt}
                            for sid, cnt in snack_counts.items()
                            if cnt > 0
                        ]
                        bestellung = svc.bestellung_service().create_order(
                            kunde_id=kunde_id,
                            tickets=ticket_data,
                            snacks=snack_data if snack_data else None,
                        )
                        ui.notify("Bestellung erfolgreich!", color="positive")
                        ui.navigate.to(f"/bestellung/{bestellung.bestellung_id}")
                    except ValueError as e:
                        err_label.set_text(str(e))
                    except Exception as e:
                        err_label.set_text(f"Fehler: {e}")

                ui.button("Jetzt bestellen", icon="shopping_cart", on_click=place_order).classes(
                    "w-full mt-2"
                ).props("unelevated color=amber size=lg")


@ui.page("/bestellung/{bestellung_id}")
def bestellung_confirm_page(bestellung_id: str) -> None:
    if not is_logged_in():
        ui.navigate.to("/login")
        return

    navbar()

    try:
        bid = UUID(bestellung_id)
    except ValueError:
        ui.navigate.to("/")
        return

    bestellung = svc.bestellung_repo().get_by_id(bid)
    if bestellung is None:
        ui.navigate.to("/")
        return

    all_snacks = {s.snack_id: s for s in svc.snack_repo().list_all()}

    with ui.column().classes("w-full max-w-2xl mx-auto px-4 py-16 items-center"):
        with ui.card().classes("bg-gray-800 rounded-2xl p-8 w-full shadow-2xl"):
            with ui.column().classes("items-center gap-4 w-full"):
                ui.icon("check_circle", size="4rem").classes("text-green-400")
                ui.label("Bestellung erfolgreich!").classes("text-2xl font-bold text-white")
                ui.label(f"Bestellnummer: {str(bid)[:8].upper()}").classes("text-gray-400 text-sm")

            ui.separator().classes("my-4 border-gray-600")

            ui.label("Ihre Tickets").classes("text-lg font-bold text-white mb-3")
            for i, ticket in enumerate(bestellung.tickets, 1):
                film = svc.film_service().get_film_details(ticket.film_id)
                with ui.card().classes("bg-gray-700 rounded-xl p-3 mb-2 w-full"):
                    ui.label(f"Ticket {i}: {film.titel if film else '–'}").classes("text-white font-semibold")
                    ui.label(
                        f"Vergünstigung: {ticket.verguenstigungsart.value.capitalize()} · "
                        f"Preis: CHF {ticket.preis:.2f}"
                    ).classes("text-gray-400 text-sm")
                    if ticket.snacks:
                        snack_lines = []
                        for ts in ticket.snacks:
                            snack = all_snacks.get(ts.snack_id)
                            if snack:
                                snack_lines.append(f"{snack.name} ×{ts.anzahl}")
                        if snack_lines:
                            ui.label("Snacks: " + ", ".join(snack_lines)).classes("text-gray-400 text-sm")

            ui.separator().classes("my-4 border-gray-600")
            with ui.row().classes("justify-between w-full items-center"):
                ui.label("Gesamtbetrag").classes("text-white font-bold text-lg")
                ui.label(f"CHF {bestellung.total_betrag:.2f}").classes("text-amber-400 font-bold text-xl")

            ui.button("Zurück zu Filmen", icon="movie", on_click=lambda: ui.navigate.to("/")).classes(
                "w-full mt-6"
            ).props("unelevated color=amber")
