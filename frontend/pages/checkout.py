from decimal import Decimal
from uuid import UUID
from datetime import datetime

from fastapi import Request
from nicegui import ui

import frontend.services as svc
from frontend.auth import get_kunde_id, is_logged_in
from frontend.components import navbar
from frontend.pdf_ticket import generate_ticket_pdf


def _platz_nr(sitz_label: str) -> str:
    """'H1' → '1',  'A10' → '10'  (führenden Buchstaben entfernen)."""
    return sitz_label.lstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz") or sitz_label

# CSS-Klassen für Sitzplatz-Farben
_SEAT_CSS = """
<style>
.seat-available .q-btn__content .q-icon { color: #3B82F6 !important; }
.seat-selected  .q-btn__content .q-icon { color: #22C55E !important; }
.seat-occupied  .q-btn__content .q-icon { color: #6B7280 !important; }
</style>
"""


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
    vorstellung = next(
        (v for v in (film.vorstellungen if film else []) if v.vorstellung_id == vid), None
    )
    if film is None or vorstellung is None:
        ui.navigate.to("/")
        return

    # Prüfen, ob die Vorstellung in der Vergangenheit liegt (Buchungen dann nicht erlaubt)
    is_past = False
    if getattr(vorstellung, "startzeit", None) is not None:
        is_past = vorstellung.startzeit < datetime.utcnow()

    all_snacks = svc.snack_repo().list_all()

    # Alle Sitze + welche davon noch frei sind
    all_seats = svc.get_all_seats_for_vorstellung(vid)
    available_ids: set[UUID] = {
        s["sitzplatz_id"] for s in svc.bestellung_service().available_seats(vid)
    }

    sektoren: dict[str, list] = {}
    for seat in all_seats:
        sektoren.setdefault(seat["sektor"], []).append(seat)

    # ── State ────────────────────────────────────────────────────────────────
    selected_seats: list[dict] = []          # {"seat_id", "seat_info", "discount"}
    snack_counts: dict[UUID, int] = {s.snack_id: 0 for s in all_snacks}
    seat_buttons: dict[UUID, ui.button] = {} # sid → NiceGUI-Button-Referenz

    DISCOUNT_OPTS = {
        "regulaer": "Regulär (±0 CHF)",
        "student":  "Student (−4.00 CHF)",
        "senior":   "Senior (−3.00 CHF)",
        "kind":     "Kind (−6.00 CHF)",
    }

    # CSS einbinden
    ui.add_head_html(_SEAT_CSS)
    navbar()

    # Falls die Vorstellung in der Vergangenheit liegt, zeige klaren Hinweis über dem Saalplan
    if is_past:
        with ui.row().classes("items-center gap-3 mb-3"):
            ui.badge("Vergangen").props("color=gray")
            ui.label("Diese Vorstellung liegt in der Vergangenheit; Buchung deaktiviert.").classes("text-gray-400 text-sm")

    with ui.column().classes("w-full max-w-5xl mx-auto px-4 py-8"):
        ui.link(f"← Zurück zu {film.titel}", f"/film/{fid}").classes(
            "text-amber-400 text-sm mb-6 block"
        )
        ui.label("Tickets buchen").classes("text-3xl font-bold text-white mb-2")

        with ui.card().classes("bg-gray-800 rounded-xl p-4 mb-6"):
            with ui.row().classes("items-center gap-6 flex-wrap"):
                with ui.column().classes("gap-1"):
                    ui.label(film.titel).classes("text-white font-bold text-lg")
                    ui.label(
                        f"{vorstellung.startzeit.strftime('%d.%m.%Y %H:%M') if vorstellung.startzeit else '–'}"
                        f" · {vorstellung.ort}, {vorstellung.saal}"
                    ).classes("text-gray-400 text-sm")
                ui.label(f"CHF {film.basispreis:.2f} / Ticket").classes(
                    "text-amber-400 font-bold text-xl ml-auto"
                )

        with ui.row().classes("w-full gap-6 flex-wrap items-start"):

            # ── Linke Spalte: Saalplan + Vergünstigungen ──────────────────────
            with ui.column().classes("flex-1 min-w-80 gap-4"):

                hint_label = ui.label("Bitte Sitzplatz(e) auswählen").classes(
                    "text-gray-400 text-sm"
                )

                # Saalplan – einmalig aufgebaut
                with ui.column().classes("items-center w-full gap-1"):
                    ui.label("Leinwand").classes("text-gray-400 text-xs tracking-widest mb-1")
                    ui.element("div").classes("w-48 h-1 bg-gray-500 rounded-full mb-3")

                    for sektor in sorted(sektoren.keys()):
                        seats_in_row = sorted(
                            sektoren[sektor],
                            key=lambda s: int(
                                "".join(filter(str.isdigit, s["sitz_label"])) or "0"
                            ),
                        )
                        with ui.row().classes("items-center gap-1"):
                            ui.label(sektor).classes(
                                "text-gray-400 text-xs font-bold w-4 text-center mr-1"
                            )
                            for seat in seats_in_row:
                                sid = seat["sitzplatz_id"]
                                is_occupied = sid not in available_ids
                                css_cls = "seat-occupied" if is_occupied else "seat-available"

                                btn = (
                                    ui.button(icon="event_seat")
                                    .props("flat dense round")
                                    .classes(css_cls)
                                    .style("font-size: 22px; width: 28px; height: 28px;")
                                )
                                seat_buttons[sid] = btn

                                # Wenn die Vorstellung in der Vergangenheit ist, dürfen keine Sitze ausgewählt werden
                                if not is_occupied and not is_past:
                                    btn.on("click", lambda s=seat: _toggle_seat(s))
                                else:
                                    btn.props("disable")

                    # Legende
                    with ui.row().classes("gap-6 mt-4 justify-center"):
                        for leg_cls, leg_color, leg_text in [
                            ("seat-available", "#3B82F6", "Verfügbar"),
                            ("seat-selected",  "#22C55E", "Ausgewählt"),
                            ("seat-occupied",  "#6B7280", "Besetzt"),
                        ]:
                            with ui.row().classes("items-center gap-1"):
                                ui.icon("event_seat").style(
                                    f"color: {leg_color}; font-size: 18px;"
                                )
                                ui.label(leg_text).classes("text-gray-300 text-xs")

                # Vergünstigungsliste (refreshable – strukturelle Änderungen)
                @ui.refreshable
                def render_discount_list() -> None:
                    if not selected_seats:
                        return
                    ui.label("Vergünstigungen").classes("text-white font-bold text-sm mb-1")
                    for i, entry in enumerate(selected_seats):
                        with ui.row().classes("items-center gap-3 w-full"):
                            ui.label(
                                f"Ticket {i + 1} – "
                                f"Reihe {entry['seat_info']['sektor']}, "
                                f"Platz {_platz_nr(entry['seat_info']['sitz_label'])}"
                            ).classes("text-gray-300 text-sm flex-1")
                            # Entferne die Kind-Option für Filme mit Altersfreigabe >= 16
                            opts = DISCOUNT_OPTS.copy()
                            if getattr(film, "altersfreigabe", 0) >= 16:
                                opts = {k: v for k, v in opts.items() if k != "kind"}

                            # Falls der Eintrag aktuell 'kind' gesetzt hat, aber nicht erlaubt ist,
                            # setze auf 'regulaer' zurück.
                            sel_value = entry.get("discount", "regulaer")
                            if sel_value == "kind" and "kind" not in opts:
                                sel_value = "regulaer"
                                entry["discount"] = sel_value

                            (
                                ui.select(options=opts, value=sel_value)
                                .props(("outlined dark color=amber dense" + (" disable" if is_past else "")))
                                .classes("w-52")
                                .on_value_change(lambda e, idx=i: _set_discount(idx, e.value))
                            )

                render_discount_list()

            # ── Rechte Spalte: Snacks + Preis + Bestellen ─────────────────────
            with ui.column().classes("w-72 gap-4 flex-shrink-0"):

                if all_snacks:
                    ui.label("Snacks").classes("text-lg font-bold text-white")
                    with ui.card().classes("bg-gray-800 rounded-xl p-4 w-full"):
                        for snack in all_snacks:
                            with ui.row().classes("items-center justify-between w-full"):
                                with ui.column().classes("gap-0"):
                                    ui.label(snack.name).classes("text-white text-sm")
                                    ui.label(f"CHF {snack.preis:.2f}").classes(
                                        "text-amber-400 text-xs"
                                    )
                                with ui.row().classes("items-center gap-1"):
                                    cnt_label = ui.label("0").classes(
                                        "text-white text-sm min-w-5 text-center"
                                    )

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
                                    ui.button(icon="remove", on_click=dec_fn).props(
                                        "flat dense color=gray round"
                                    )
                                    ui.button(icon="add", on_click=inc_fn).props(
                                        "flat dense color=amber round"
                                    )

                ui.label("Preisübersicht").classes("text-lg font-bold text-white mt-2")
                with ui.card().classes("bg-gray-800 rounded-xl p-4 w-full"):
                    total_label = ui.label("CHF 0.00").classes("text-2xl font-bold text-amber-400")
                    detail_label = ui.label("Noch kein Sitzplatz gewählt").classes(
                        "text-gray-400 text-sm"
                    )

                err_label = ui.label("").classes("text-red-400 text-sm mt-1")

                ui.button(
                    "Jetzt bestellen", icon="shopping_cart", on_click=lambda: _place_order()
                ).classes("w-full mt-2").props("unelevated color=amber size=lg" + (" disable" if is_past else ""))

    # ── Hilfsfunktionen ───────────────────────────────────────────────────────

    def _update_total() -> None:
        discounts = {"regulaer": 0, "student": -4, "senior": -3, "kind": -6}
        ticket_total = Decimal("0.00")
        lines = []
        for i, entry in enumerate(selected_seats):
            tp = film.basispreis + Decimal(discounts.get(entry["discount"], 0))
            ticket_total += tp
            lines.append(f"Ticket {i + 1}: CHF {tp:.2f}")
        snack_total = sum(
            s.preis * snack_counts[s.snack_id] for s in all_snacks if snack_counts[s.snack_id] > 0
        )
        for s in all_snacks:
            if snack_counts[s.snack_id] > 0:
                lines.append(
                    f"{s.name} ×{snack_counts[s.snack_id]}: "
                    f"CHF {s.preis * snack_counts[s.snack_id]:.2f}"
                )
        total = ticket_total + snack_total
        total_label.set_text(f"CHF {total:.2f}")
        detail_label.set_text(" | ".join(lines) if lines else "Noch kein Sitzplatz gewählt")

    def _toggle_seat(seat_info: dict) -> None:
        sid = seat_info["sitzplatz_id"]
        existing = next(
            (i for i, e in enumerate(selected_seats) if e["seat_id"] == sid), None
        )

        btn = seat_buttons.get(sid)

        if existing is not None:
            # Abwählen → blau
            selected_seats.pop(existing)
            if btn:
                btn.classes(remove="seat-selected", add="seat-available")
        else:
            # Auswählen → grün
            selected_seats.append(
                {"seat_id": sid, "seat_info": seat_info, "discount": "regulaer"}
            )
            if btn:
                btn.classes(remove="seat-available", add="seat-selected")

        n = len(selected_seats)
        if n == 0:
            hint_label.set_text("Bitte Sitzplatz(e) auswählen")
        elif n == 1:
            hint_label.set_text("1 Sitzplatz ausgewählt")
        else:
            hint_label.set_text(f"{n} Sitzplätze ausgewählt")

        render_discount_list.refresh()
        _update_total()

    def _set_discount(ticket_idx: int, discount: str) -> None:
        if ticket_idx < len(selected_seats):
            selected_seats[ticket_idx]["discount"] = discount
        _update_total()

    def _place_order() -> None:
        if is_past:
            err_label.set_text("Vorstellung liegt bereits in der Vergangenheit. Buchung nicht möglich.")
            return
        if not selected_seats:
            err_label.set_text("Bitte mindestens einen Sitzplatz auswählen.")
            return
        err_label.set_text("")
        try:
            ticket_data = [
                {
                    "film_id": fid,
                    "vorstellung_id": vid,
                    "sitzplatz_id": entry["seat_id"],
                    "verguenstigungsart": entry["discount"],
                }
                for entry in selected_seats
            ]
            snack_data = [
                {"ticket_index": 0, "snack_id": s_id, "anzahl": cnt}
                for s_id, cnt in snack_counts.items()
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

    film_vorstellung_map: dict = {}
    sitzplatz_map: dict = {}

    for ticket in bestellung.tickets:
        if ticket.vorstellung_id not in film_vorstellung_map:
            film = svc.film_service().get_film_details(ticket.film_id)
            if film:
                v = next(
                    (v for v in film.vorstellungen if v.vorstellung_id == ticket.vorstellung_id),
                    None,
                )
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

    with ui.column().classes("w-full max-w-2xl mx-auto px-4 py-16 items-center"):
        with ui.card().classes("bg-gray-800 rounded-2xl p-8 w-full shadow-2xl"):
            with ui.column().classes("items-center gap-4 w-full"):
                ui.icon("check_circle", size="4rem").classes("text-green-400")
                ui.label("Bestellung erfolgreich!").classes("text-2xl font-bold text-white")

            ui.separator().classes("my-4 border-gray-600")

            bid_short = str(bid)[:8].upper()
            order_date = bestellung.bestellungsdatum.strftime("%d.%m.%Y")
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
                disc_key = (
                    ticket.verguenstigungsart.value
                    if hasattr(ticket.verguenstigungsart, "value")
                    else str(ticket.verguenstigungsart)
                )

                with ui.card().classes("bg-gray-700 rounded-xl p-3 mb-2 w-full"):
                    ui.label(f"Ticket {i}: {fv.get('titel', '–')}").classes(
                        "text-white font-semibold"
                    )
                    startzeit = fv.get("startzeit")
                    if startzeit and hasattr(startzeit, "strftime"):
                        ui.label(
                            f"{startzeit.strftime('%d.%m.%Y %H:%M')} · "
                            f"{fv.get('ort', '–')}, {fv.get('saal', '–')}"
                        ).classes("text-gray-400 text-sm")
                    if sitz:
                        ui.label(
                            f"Reihe {sitz.get('sektor', '–')}, "
                            f"Platz {_platz_nr(sitz.get('sitz_label', '–'))}"
                        ).classes("text-gray-400 text-sm")
                    ui.label(
                        f"Vergünstigung: {disc_map.get(disc_key, disc_key.capitalize())} · "
                        f"Preis: CHF {ticket.preis:.2f}"
                    ).classes("text-gray-400 text-sm")

            # ── Snacks (aggregiert, nach allen Tickets) ───────────────────
            all_snack_lines: dict = {}
            for ticket in bestellung.tickets:
                for ts in ticket.snacks:
                    snack = all_snacks.get(ts.snack_id)
                    if snack:
                        if ts.snack_id in all_snack_lines:
                            all_snack_lines[ts.snack_id] = (snack, all_snack_lines[ts.snack_id][1] + ts.anzahl)
                        else:
                            all_snack_lines[ts.snack_id] = (snack, ts.anzahl)

            if all_snack_lines:
                ui.separator().classes("my-3 border-gray-700")
                ui.label("Snacks").classes("text-white font-bold text-sm mb-1")
                for snack, anzahl in all_snack_lines.values():
                    with ui.row().classes("justify-between w-full"):
                        ui.label(f"{anzahl}x {snack.name}").classes("text-gray-300 text-sm")
                        ui.label(f"CHF {snack.preis * anzahl:.2f}").classes("text-amber-400 text-sm")

            ui.separator().classes("my-4 border-gray-600")
            with ui.row().classes("justify-between w-full items-center"):
                ui.label("Gesamtbetrag").classes("text-white font-bold text-lg")
                ui.label(f"CHF {bestellung.total_betrag:.2f}").classes(
                    "text-amber-400 font-bold text-xl"
                )

            ui.separator().classes("my-4 border-gray-600")

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
                ui.button(
                    "PDF-Ticket herunterladen", icon="picture_as_pdf", on_click=download_pdf
                ).classes("flex-1").props("unelevated color=amber")
                ui.button(
                    "Zurück zu Filmen", icon="movie", on_click=lambda: ui.navigate.to("/")
                ).classes("flex-1").props("outline color=amber")
