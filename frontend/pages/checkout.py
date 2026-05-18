from decimal import Decimal
from uuid import UUID

from fastapi import Request
from nicegui import ui

import frontend.services as svc
from frontend.auth import get_kunde_id, is_logged_in
from frontend.components import navbar
from frontend.pdf_ticket import generate_ticket_pdf


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

    # Sitze nach Sektor gruppieren (einmalig)
    sektoren: dict[str, list] = {}
    for seat in available_seats:
        sektoren.setdefault(seat["sektor"], []).append(seat)

    # ── State ────────────────────────────────────────────────────────────────
    # Jedes Ticket: {"seat_id": UUID|None, "discount": str, "seat_label": str}
    ticket_states: list[dict] = [{"seat_id": None, "discount": "regulaer", "seat_label": ""}]
    snack_counts: dict[UUID, int] = {s.snack_id: 0 for s in all_snacks}

    # ── UI aufbauen ───────────────────────────────────────────────────────────
    navbar()

    with ui.column().classes("w-full max-w-5xl mx-auto px-4 py-8"):
        ui.link(f"← Zurück zu {film.titel}", f"/film/{fid}").classes("text-amber-400 text-sm mb-6 block")
        ui.label("Tickets buchen").classes("text-3xl font-bold text-white mb-2")

        # Vorstellungsinfo
        with ui.card().classes("bg-gray-800 rounded-xl p-4 mb-6"):
            with ui.row().classes("items-center gap-6 flex-wrap"):
                with ui.column().classes("gap-1"):
                    ui.label(film.titel).classes("text-white font-bold text-lg")
                    ui.label(
                        f"{vorstellung.startzeit.strftime('%d.%m.%Y %H:%M') if vorstellung.startzeit else '–'} · "
                        f"{vorstellung.ort}, {vorstellung.saal}"
                    ).classes("text-gray-400 text-sm")
                ui.label(f"CHF {film.basispreis:.2f} / Ticket").classes("text-amber-400 font-bold text-xl ml-auto")

        with ui.row().classes("w-full gap-6 flex-wrap items-start"):

            # ── Linke Spalte: Tickets ─────────────────────────────────────────
            with ui.column().classes("flex-1 min-w-80 gap-3"):
                ui.label("Tickets").classes("text-xl font-bold text-white")

                tickets_area = ui.element("div").classes("flex flex-col gap-4 w-full")

                add_ticket_btn = ui.button(
                    "Ticket hinzufügen", icon="add", on_click=lambda: add_ticket()
                ).props("flat color=amber").classes("mt-1 self-start")

            # ── Rechte Spalte: Snacks + Preisübersicht + Bestellen ────────────
            with ui.column().classes("w-72 gap-4 flex-shrink-0"):

                if all_snacks:
                    ui.label("Snacks").classes("text-lg font-bold text-white")
                    with ui.card().classes("bg-gray-800 rounded-xl p-4 w-full"):
                        snack_counters: dict[UUID, ui.label] = {}
                        for snack in all_snacks:
                            with ui.row().classes("items-center justify-between w-full"):
                                with ui.column().classes("gap-0"):
                                    ui.label(snack.name).classes("text-white text-sm")
                                    ui.label(f"CHF {snack.preis:.2f}").classes("text-amber-400 text-xs")
                                with ui.row().classes("items-center gap-1"):
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

                ui.label("Preisübersicht").classes("text-lg font-bold text-white mt-2")
                with ui.card().classes("bg-gray-800 rounded-xl p-4 w-full"):
                    total_label = ui.label(f"CHF {film.basispreis:.2f}").classes(
                        "text-2xl font-bold text-amber-400"
                    )
                    detail_label = ui.label(f"Ticket 1: CHF {film.basispreis:.2f}").classes(
                        "text-gray-400 text-sm"
                    )

                err_label = ui.label("").classes("text-red-400 text-sm mt-1")

                ui.button(
                    "Jetzt bestellen", icon="shopping_cart", on_click=lambda: place_order()
                ).classes("w-full mt-2").props("unelevated color=amber size=lg")

    # ── Funktionen ────────────────────────────────────────────────────────────

    def _update_total() -> None:
        discounts = {"regulaer": 0, "student": -4, "senior": -3, "kind": -6}
        ticket_total = Decimal("0.00")
        lines = []
        for i, ts in enumerate(ticket_states):
            tp = film.basispreis + Decimal(discounts.get(ts["discount"], 0))
            ticket_total += tp
            lines.append(f"Ticket {i + 1}: CHF {tp:.2f}")
        snack_total = sum(
            s.preis * snack_counts[s.snack_id] for s in all_snacks if snack_counts[s.snack_id] > 0
        )
        for s in all_snacks:
            if snack_counts[s.snack_id] > 0:
                lines.append(
                    f"{s.name} ×{snack_counts[s.snack_id]}: CHF {s.preis * snack_counts[s.snack_id]:.2f}"
                )
        total = ticket_total + snack_total
        total_label.set_text(f"CHF {total:.2f}")
        detail_label.set_text(" | ".join(lines))

    def _render_ticket_card(idx: int, taken: set) -> None:
        ts = ticket_states[idx]
        discount_opts = {
            "regulaer": "Regulär (±0 CHF)",
            "student": "Student (−4.00 CHF)",
            "senior": "Senior (−3.00 CHF)",
            "kind": "Kind (−6.00 CHF)",
        }

        with ui.card().classes("bg-gray-800 rounded-xl p-4 w-full"):
            # Ticket-Header
            with ui.row().classes("justify-between items-center mb-3"):
                ui.label(f"Ticket {idx + 1}").classes("text-amber-400 font-bold text-base")
                if len(ticket_states) > 1:
                    ui.button(
                        icon="delete", on_click=lambda i=idx: remove_ticket(i)
                    ).props("flat dense round color=red-4").classes("ml-auto")

            # Gewählter Sitzplatz
            if ts["seat_label"]:
                ui.label(f"✓ {ts['seat_label']}").classes("text-green-400 text-sm mb-2 font-semibold")
            else:
                ui.label("Kein Sitzplatz ausgewählt").classes("text-gray-500 text-sm mb-2")

            # Sitzplatz-Auswahl
            if not available_seats:
                ui.label("Keine freien Sitzplätze verfügbar.").classes("text-red-400 text-sm")
            else:
                for sektor, seats in sektoren.items():
                    ui.label(f"Reihe {sektor}").classes("text-gray-400 text-xs font-semibold uppercase mt-2")
                    with ui.row().classes("flex-wrap gap-1"):
                        for seat in seats:
                            sid = seat["sitzplatz_id"]
                            is_selected = sid == ts["seat_id"]
                            is_taken_by_other = sid in taken and not is_selected

                            if is_taken_by_other:
                                ui.button(seat["sitz_label"]).props(
                                    "disable dense outline color=gray"
                                ).classes("min-w-10 opacity-30 text-xs")
                            else:
                                btn_props = ("unelevated color=amber" if is_selected else "outline color=amber") + " dense"
                                ui.button(
                                    seat["sitz_label"],
                                    on_click=lambda s=seat, i=idx: select_seat(i, s),
                                ).props(btn_props).classes("min-w-10 text-xs")

            # Vergünstigung
            ui.label("Vergünstigung").classes("text-gray-400 text-xs font-semibold uppercase mt-3 mb-1")
            (
                ui.select(options=discount_opts, value=ts["discount"])
                .props("outlined dark color=amber dense")
                .classes("w-full")
                .on_value_change(lambda e, i=idx: _set_discount(i, e.value))
            )

    def render_all_tickets() -> None:
        tickets_area.clear()
        taken = {ts["seat_id"] for ts in ticket_states if ts["seat_id"]}
        with tickets_area:
            for idx in range(len(ticket_states)):
                _render_ticket_card(idx, taken)
        _update_total()

    def select_seat(ticket_idx: int, seat_info: dict) -> None:
        ticket_states[ticket_idx]["seat_id"] = seat_info["sitzplatz_id"]
        ticket_states[ticket_idx]["seat_label"] = (
            f"Reihe {seat_info['sektor']}, Platz {seat_info['sitz_label']}"
        )
        render_all_tickets()

    def _set_discount(ticket_idx: int, discount: str) -> None:
        ticket_states[ticket_idx]["discount"] = discount
        _update_total()

    def add_ticket() -> None:
        taken = {ts["seat_id"] for ts in ticket_states if ts["seat_id"]}
        free_count = sum(1 for s in available_seats if s["sitzplatz_id"] not in taken)
        if free_count == 0:
            ui.notify("Keine weiteren freien Sitzplätze verfügbar.", color="warning")
            return
        ticket_states.append({"seat_id": None, "discount": "regulaer", "seat_label": ""})
        render_all_tickets()

    def remove_ticket(idx: int) -> None:
        ticket_states.pop(idx)
        render_all_tickets()

    def place_order() -> None:
        for i, ts in enumerate(ticket_states):
            if ts["seat_id"] is None:
                err_label.set_text(f"Bitte für Ticket {i + 1} einen Sitzplatz auswählen.")
                return
        # Doppelte Sitzplätze prüfen
        seen: set[UUID] = set()
        for i, ts in enumerate(ticket_states):
            if ts["seat_id"] in seen:
                err_label.set_text(f"Ticket {i + 1}: Sitzplatz bereits durch ein anderes Ticket belegt.")
                return
            seen.add(ts["seat_id"])
        err_label.set_text("")
        try:
            ticket_data = [
                {
                    "film_id": fid,
                    "vorstellung_id": vid,
                    "sitzplatz_id": ts["seat_id"],
                    "verguenstigungsart": ts["discount"],
                }
                for ts in ticket_states
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

    # Erstes Rendering
    render_all_tickets()


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

    # Hilfs-Maps für PDF und Anzeige aufbauen
    film_vorstellung_map: dict = {}
    sitzplatz_map: dict = {}
    film_map: dict = {}

    for ticket in bestellung.tickets:
        if ticket.vorstellung_id not in film_vorstellung_map:
            film = svc.film_service().get_film_details(ticket.film_id)
            if film:
                film_map[ticket.film_id] = film
                v = next((v for v in film.vorstellungen if v.vorstellung_id == ticket.vorstellung_id), None)
                film_vorstellung_map[ticket.vorstellung_id] = {
                    "titel": film.titel,
                    "startzeit": v.startzeit if v else None,
                    "ort": v.ort if v else "–",
                    "saal": v.saal if v else "–",
                }
        if ticket.sitzplatz_id not in sitzplatz_map:
            info = svc.get_sitzplatz_info(ticket.sitzplatz_id)
            if info:
                sitzplatz_map[ticket.sitzplatz_id] = info

    # ── UI ───────────────────────────────────────────────────────────────────
    with ui.column().classes("w-full max-w-2xl mx-auto px-4 py-16 items-center"):
        with ui.card().classes("bg-gray-800 rounded-2xl p-8 w-full shadow-2xl"):
            with ui.column().classes("items-center gap-4 w-full"):
                ui.icon("check_circle", size="4rem").classes("text-green-400")
                ui.label("Bestellung erfolgreich!").classes("text-2xl font-bold text-white")

            ui.separator().classes("my-4 border-gray-600")

            # Bestellmetadaten
            bid_short = str(bid)[:8].upper()
            order_date = bestellung.bestellungsdatum.strftime("%d.%m.%Y %H:%M")
            with ui.row().classes("justify-between w-full text-sm mb-2"):
                ui.label(f"Bestellnummer: {bid_short}").classes("text-gray-400")
                ui.label(f"Datum: {order_date}").classes("text-gray-400")

            ui.separator().classes("my-2 border-gray-700")
            ui.label("Ihre Tickets").classes("text-lg font-bold text-white mb-3")

            for i, ticket in enumerate(bestellung.tickets, 1):
                fv = film_vorstellung_map.get(ticket.vorstellung_id, {})
                sitz = sitzplatz_map.get(ticket.sitzplatz_id, {})
                disc_map = {
                    "regulaer": "Regulär", "student": "Student",
                    "senior": "Senior", "kind": "Kind",
                }
                disc_key = ticket.verguenstigungsart.value if hasattr(ticket.verguenstigungsart, "value") else str(ticket.verguenstigungsart)

                with ui.card().classes("bg-gray-700 rounded-xl p-3 mb-2 w-full"):
                    ui.label(f"Ticket {i}: {fv.get('titel', '–')}").classes("text-white font-semibold")
                    startzeit = fv.get("startzeit")
                    if startzeit and hasattr(startzeit, "strftime"):
                        ui.label(f"{startzeit.strftime('%d.%m.%Y %H:%M')} · {fv.get('ort', '–')}, {fv.get('saal', '–')}").classes("text-gray-400 text-sm")
                    if sitz:
                        ui.label(f"Sitzplatz: Reihe {sitz.get('sektor', '–')}, Platz {sitz.get('sitz_label', '–')}").classes("text-gray-400 text-sm")
                    ui.label(
                        f"Vergünstigung: {disc_map.get(disc_key, disc_key.capitalize())} · Preis: CHF {ticket.preis:.2f}"
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

            ui.separator().classes("my-4 border-gray-600")

            # PDF-Download
            def download_pdf() -> None:
                try:
                    pdf_bytes = generate_ticket_pdf(
                        bestellung=bestellung,
                        snacks_map=all_snacks,
                        film_vorstellung_map=film_vorstellung_map,
                        sitzplatz_map=sitzplatz_map,
                    )
                    ui.download(pdf_bytes, filename=f"ticket_{bid_short}.pdf")
                except Exception as e:
                    ui.notify(f"PDF-Fehler: {e}", color="negative")

            with ui.row().classes("w-full gap-3 mt-2"):
                ui.button("PDF-Ticket herunterladen", icon="picture_as_pdf", on_click=download_pdf).classes(
                    "flex-1"
                ).props("unelevated color=amber")
                ui.button("Zurück zu Filmen", icon="movie", on_click=lambda: ui.navigate.to("/")).classes(
                    "flex-1"
                ).props("outline color=amber")
