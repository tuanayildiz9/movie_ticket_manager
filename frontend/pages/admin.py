from datetime import date, datetime
from datetime import timedelta
from decimal import Decimal
from uuid import UUID


def _parse_date(val) -> date | None:
    if val is None:
        return None
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    try:
        return date.fromisoformat(str(val))
    except (ValueError, TypeError):
        try:
            return datetime.strptime(str(val), "%d.%m.%Y").date()
        except (ValueError, TypeError):
            return None


def _apply_german_date_picker(date_input) -> None:
    date_input.picker.props['mask'] = 'DD.MM.YYYY'
    date_input.picker.props[':locale'] = "{days:['Sonntag','Montag','Dienstag','Mittwoch','Donnerstag','Freitag','Samstag'],daysShort:['So','Mo','Di','Mi','Do','Fr','Sa'],months:['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'],monthsShort:['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez'],firstDayOfWeek:1}"


def _overlaps(existing_start: datetime, existing_end: datetime, new_start: datetime, new_end: datetime) -> bool:
    return new_start < existing_end and new_end > existing_start

from nicegui import ui


import frontend.services as svc
from frontend.auth import get_account_id, is_admin, is_logged_in
from frontend.components import navbar
from backend.models import Film


def _format_admin_date(value: date | datetime | None) -> str:
    if not value:
        return "–"
    if isinstance(value, datetime):
        value = value.date()
    return value.strftime("%d.%m.%Y")


@ui.page("/admin")
def admin_page() -> None:
    if not is_logged_in() or not is_admin():
        ui.navigate.to("/")
        return

    navbar()

    account_id = get_account_id()

    with ui.column().classes("w-full max-w-6xl mx-auto px-4 py-8"):
        ui.label("Admin-Panel").classes("text-3xl font-bold text-white mb-6")

        with ui.tabs().classes("text-amber-400") as tabs:
            ui.tab("filme", label="Filme", icon="movie")
            ui.tab("vorstellungen", label="Vorstellungen", icon="event")
            ui.tab("umsatz", label="Umsatz", icon="bar_chart")

        with ui.tab_panels(tabs, value="filme").classes("w-full mt-4"):
            with ui.tab_panel("filme"):
                _filme_tab(account_id)
            with ui.tab_panel("vorstellungen"):
                _vorstellungen_tab(account_id)
            with ui.tab_panel("umsatz"):
                _umsatz_tab()


def _filme_tab(account_id: UUID | None) -> None:
    ui.label("Filmverwaltung").classes("text-xl font-bold text-white mb-4")

    table_container = ui.element("div").classes("w-full")

    def reload_table() -> None:
        table_container.clear()
        all_films = svc.film_service().list_all_films()
        with table_container:
            columns = [
                {"name": "titel", "label": "Titel", "field": "titel", "align": "left", "sortable": True},
                {"name": "altersfreigabe", "label": "FSK", "field": "altersfreigabe", "align": "center"},
                {"name": "basispreis", "label": "Preis", "field": "basispreis", "align": "right"},
                {"name": "erscheinungsdatum", "label": "Erscheinung", "field": "erscheinungsdatum", "align": "center"},
                {"name": "aktiv", "label": "Aktiv", "field": "aktiv", "align": "center"},
                {"name": "aktionen", "label": "Aktionen", "field": "aktionen", "align": "center"},
            ]
            rows = [
                {
                    "id": str(f.film_id),
                    "titel": f.titel,
                    "altersfreigabe": f.altersfreigabe,
                    "basispreis": f"CHF {f.basispreis:.2f}",
                    "erscheinungsdatum": _format_admin_date(f.erscheinungsdatum),
                    "aktiv": "✓" if f.aktiv else "✗",
                }
                for f in all_films
            ]
            table = ui.table(columns=columns, rows=rows, row_key="id").classes(
                "w-full bg-gray-800 text-white rounded-xl"
            ).props("dark flat")

            table.add_slot(
                "body-cell-aktionen",
                r"""
                <q-td :props="props">
                    <q-btn flat dense icon="edit" color="amber"
                        @click="$parent.$emit('edit', props.row)" />
                    <q-btn flat dense icon="delete" color="red"
                        @click="$parent.$emit('delete', props.row)" />
                </q-td>
                """,
            )

            def on_edit(e) -> None:
                film_id = UUID(e.args["id"])
                film = svc.film_service().get_film_details(film_id)
                if film:
                    _edit_film_dialog(film, account_id, reload_table)

            def on_delete(e) -> None:
                film_id = UUID(e.args["id"])
                film_titel = e.args["titel"]
                _confirm_delete_film(film_id, film_titel, account_id, reload_table)

            table.on("edit", on_edit)
            table.on("delete", on_delete)

    reload_table()

    ui.button("Neuen Film erstellen", icon="add", on_click=lambda: _create_film_dialog(account_id, reload_table)).props(
        "unelevated color=amber"
    ).classes("mt-4")


def _vorstellungen_tab(account_id: UUID | None) -> None:
    ui.label("Vorstellungsverwaltung").classes("text-xl font-bold text-white mb-4")

    all_films = svc.film_service().list_all_films()
    film_options = {str(f.film_id): f.titel for f in all_films}
    selected_film: dict[str, UUID | None] = {"id": None}

    film_sel = (
        ui.select(options=film_options, label="Film auswählen", with_input=True)
        .props("outlined dark color=amber")
        .classes("w-72")
    )

    container = ui.element("div").classes("w-full mt-4")

    def load_vorstellungen() -> None:
        if not film_sel.value:
            return
        film_id = UUID(film_sel.value)
        selected_film["id"] = film_id
        film = svc.film_service().get_film_details(film_id)
        container.clear()
        with container:
            if not film or not film.vorstellungen:
                ui.label("Keine Vorstellungen.").classes("text-gray-500")
                return
            for v in film.vorstellungen:
                with ui.card().classes("bg-gray-800 rounded-xl p-4 mb-3"):
                    with ui.row().classes("items-center justify-between flex-wrap gap-3"):
                        with ui.column().classes("gap-1"):
                            ui.label(
                                v.startzeit.strftime("%d.%m.%Y %H:%M") if v.startzeit else "–"
                            ).classes("text-white font-semibold")
                            ui.label(f"{v.ort} · {v.saal}").classes("text-gray-400 text-sm")
                            ui.label(
                                f"{v.free_seat_count()} frei / {len(v.sitzplaetze)} gesamt"
                            ).classes("text-gray-400 text-sm")
                        with ui.row().classes("gap-2"):
                            vid = v.vorstellung_id

                            def edit_v(vorstellung_id=vid):
                                _edit_vorstellung_dialog(vorstellung_id, account_id, load_vorstellungen)

                            def del_v(vorstellung_id=vid):
                                _confirm_delete_vorstellung(vorstellung_id, account_id, load_vorstellungen)

                            ui.button(icon="edit", on_click=edit_v).props("flat dense color=amber")
                            ui.button(icon="delete", on_click=del_v).props("flat dense color=red")

    film_sel.on_value_change(lambda _: load_vorstellungen())

    def new_vorstellung() -> None:
        if not selected_film["id"]:
            ui.notify("Bitte zuerst einen Film auswählen.", color="warning")
            return
        _create_vorstellung_dialog(selected_film["id"], account_id, load_vorstellungen)

    ui.button("Neue Vorstellung", icon="add", on_click=new_vorstellung).props("unelevated color=amber").classes("mt-3")


def _umsatz_tab() -> None:
    ui.label("Umsatzübersicht").classes("text-xl font-bold text-white mb-4")

    # ── Gesamtübersicht ───────────────────────────────────────────────────────
    try:
        all_orders = svc.bestellung_service().list_all_orders()
        total_umsatz = sum(o.total_betrag for o in all_orders)
        total_tickets = sum(o.anzahl_tickets for o in all_orders)
        total_orders = len(all_orders)

        with ui.row().classes("gap-4 flex-wrap mb-6"):
            with ui.card().classes("bg-amber-700 rounded-xl p-5 text-center min-w-40"):
                ui.label(f"CHF {total_umsatz:.2f}").classes("text-3xl font-bold text-white")
                ui.label("Gesamtumsatz").classes("text-amber-100 text-sm mt-1")
            with ui.card().classes("bg-gray-700 rounded-xl p-5 text-center min-w-40"):
                ui.label(str(total_tickets)).classes("text-3xl font-bold text-white")
                ui.label("Tickets gesamt").classes("text-gray-300 text-sm mt-1")
            with ui.card().classes("bg-gray-700 rounded-xl p-5 text-center min-w-40"):
                ui.label(str(total_orders)).classes("text-3xl font-bold text-white")
                ui.label("Bestellungen").classes("text-gray-300 text-sm mt-1")
    except Exception as e:
        ui.label(f"Fehler beim Laden der Gesamtübersicht: {e}").classes("text-red-400 text-sm mb-4")

    ui.separator().classes("my-4 border-gray-600")

    # ── Umsatz pro Film ───────────────────────────────────────────────────────
    ui.label("Umsatz pro Film").classes("text-lg font-bold text-white mb-3")
    try:
        all_films = svc.film_service().list_all_films()
        film_rows = []
        for f in all_films:
            orders_for_film = svc.bestellung_service().list_orders_by_film(f.film_id)
            tickets_sold = sum(len(o.tickets) for o in orders_for_film)
            umsatz_film = sum(
                sum(t.preis for t in o.tickets if t.film_id == f.film_id)
                for o in orders_for_film
            )
            film_rows.append({
                "id": str(f.film_id),
                "titel": f.titel,
                "tickets": tickets_sold,
                "umsatz": f"CHF {umsatz_film:.2f}",
                "aktiv": "✓" if f.aktiv else "✗",
            })
        # Sortiert nach Umsatz (höchster zuerst)
        film_rows.sort(key=lambda x: x["umsatz"], reverse=True)
        ui.table(
            columns=[
                {"name": "titel", "label": "Film", "field": "titel", "align": "left", "sortable": True},
                {"name": "tickets", "label": "Tickets", "field": "tickets", "align": "center", "sortable": True},
                {"name": "umsatz", "label": "Umsatz", "field": "umsatz", "align": "right", "sortable": True},
                {"name": "aktiv", "label": "Aktiv", "field": "aktiv", "align": "center"},
            ],
            rows=film_rows,
            row_key="id",
        ).classes("w-full bg-gray-800 text-white rounded-xl mb-6").props("dark flat")
    except Exception as e:
        ui.label(f"Fehler: {e}").classes("text-red-400 text-sm mb-4")

    ui.separator().classes("my-4 border-gray-600")

    # ── Detail pro Film (aufklappbar) ─────────────────────────────────────────
    ui.label("Detail-Ansicht pro Film").classes("text-lg font-bold text-white mb-3")

    all_films_detail = svc.film_service().list_all_films()
    film_options = {str(f.film_id): f.titel for f in all_films_detail}

    film_sel = (
        ui.select(options=film_options, label="Film auswählen", with_input=True)
        .props("outlined dark color=amber")
        .classes("w-72")
    )

    result_area = ui.element("div").classes("w-full mt-4")

    def load_detail() -> None:
        if not film_sel.value:
            return
        try:
            overview = svc.admin_service().get_sales_overview(UUID(film_sel.value))
            result_area.clear()
            with result_area:
                with ui.row().classes("gap-4 flex-wrap mb-4"):
                    with ui.card().classes("bg-amber-800 rounded-xl p-4 text-center"):
                        ui.label(str(overview["verkaufte_tickets"])).classes("text-2xl font-bold text-white")
                        ui.label("Tickets verkauft").classes("text-amber-200 text-sm")
                    with ui.card().classes("bg-gray-700 rounded-xl p-4 text-center"):
                        ui.label(str(overview["freie_plaetze"])).classes("text-2xl font-bold text-white")
                        ui.label("Freie Plätze").classes("text-gray-300 text-sm")

                if overview["vorstellungen"]:
                    ui.label("Vorstellungen").classes("text-base font-bold text-white mt-2 mb-2")
                    columns = [
                        {"name": "startzeit", "label": "Zeit", "field": "startzeit", "align": "left"},
                        {"name": "ort", "label": "Ort / Saal", "field": "ort", "align": "left"},
                        {"name": "verkauft", "label": "Verkauft", "field": "verkauft", "align": "center"},
                        {"name": "frei", "label": "Frei", "field": "frei", "align": "center"},
                    ]
                    rows = [
                        {
                            "id": str(v["vorstellung_id"]),
                            "startzeit": v["startzeit"].strftime("%d.%m.%Y %H:%M") if v["startzeit"] else "–",
                            "ort": f"{v['ort']} · {v['saal']}",
                            "verkauft": v["verkaufte_tickets"],
                            "frei": v["freie_plaetze"],
                        }
                        for v in overview["vorstellungen"]
                    ]
                    ui.table(columns=columns, rows=rows, row_key="id").classes(
                        "w-full bg-gray-800 text-white rounded-xl"
                    ).props("dark flat")
        except Exception as e:
            result_area.clear()
            with result_area:
                ui.label(f"Fehler: {e}").classes("text-red-400")

    film_sel.on_value_change(lambda _: load_detail())


# --- Dialogs ---

def _create_film_dialog(account_id: UUID | None, on_done) -> None:
    kategorien = svc.get_all_kategorien()
    sprachen = svc.get_all_sprachen()
    kat_id_map = {item["name"]: item["id"] for item in kategorien}
    spr_id_map = {item["name"]: item["id"] for item in sprachen}

    with ui.dialog() as dialog, ui.card().classes("bg-gray-800 min-w-[500px] max-w-2xl"):
        ui.label("Neuen Film erstellen").classes("text-xl font-bold text-amber-400 mb-4")

        titel_in = ui.input("Titel").classes("w-full").props("outlined dark color=amber")
        beschreibung_in = (
            ui.textarea("Beschreibung").classes("w-full mt-3").props("outlined dark color=amber rows=3")
        )
        hauptdarsteller_in = (
            ui.input("Hauptdarsteller").classes("w-full mt-3").props("outlined dark color=amber")
        )
        coverbild_in = (
            ui.input("Cover-URL").classes("w-full mt-3").props("outlined dark color=amber")
        )
        with ui.row().classes("w-full gap-3 mt-3"):
            fsk_in = ui.number("Altersfreigabe", value=0, min=0, max=18).props("outlined dark color=amber").classes("w-32")
            preis_in = ui.number("Preis (CHF)", value=12.00, min=0, step=0.5, format="%.2f").props(
                "outlined dark color=amber"
            ).classes("flex-1")

        datum_in = _date_picker("Erscheinungsdatum", value=date.today()).classes("w-full mt-3")

        kat_sel = (
            ui.select(
                label="Kategorien",
                options={k["name"]: k["name"] for k in kategorien},
                multiple=True,
            )
            .classes("w-full mt-3")
            .props("outlined dark color=amber")
        )
        spr_sel = (
            ui.select(
                label="Sprachen",
                options={s["name"]: s["name"] for s in sprachen},
                multiple=True,
            )
            .classes("w-full mt-3")
            .props("outlined dark color=amber")
        )

        err = ui.label("").classes("text-red-400 text-sm mt-2")

        def create() -> None:
            try:
                erschein = datum_in.value or date.today()
                kat_ids = [kat_id_map[n] for n in (kat_sel.value or []) if n in kat_id_map]
                spr_ids = [spr_id_map[n] for n in (spr_sel.value or []) if n in spr_id_map]

                film = Film(
                    titel=titel_in.value.strip(),
                    beschreibung=beschreibung_in.value.strip(),
                    hauptdarsteller=hauptdarsteller_in.value.strip(),
                    coverbild_url=coverbild_in.value.strip(),
                    altersfreigabe=int(fsk_in.value or 0),
                    basispreis=Decimal(str(preis_in.value or 0)),
                    erscheinungsdatum=erschein,
                    aktiv=True,
                    kategorie_ids=kat_ids,
                    sprache_ids=spr_ids,
                )
                svc.admin_service().create_film(account_id, film)
                ui.notify("Film erstellt!", color="positive")
                dialog.close()
                on_done()
            except Exception as e:
                err.set_text(str(e))

        with ui.row().classes("justify-end gap-2 mt-4"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat color=gray")
            ui.button("Erstellen", on_click=create).props("unelevated color=amber")

    dialog.open()


def _edit_film_dialog(film: Film, account_id: UUID | None, on_done) -> None:
    with ui.dialog() as dialog, ui.card().classes("bg-gray-800 min-w-96"):
        ui.label("Film bearbeiten").classes("text-xl font-bold text-amber-400 mb-4")

        titel_in = ui.input("Titel", value=film.titel).classes("w-full").props("outlined dark color=amber")
        beschreibung_in = (
            ui.textarea("Beschreibung", value=film.beschreibung or "")
            .classes("w-full mt-3")
            .props("outlined dark color=amber rows=3")
        )
        hauptdarsteller_in = (
            ui.input("Hauptdarsteller", value=film.hauptdarsteller or "")
            .classes("w-full mt-3")
            .props("outlined dark color=amber")
        )
        coverbild_in = (
            ui.input("Cover-URL", value=film.coverbild_url or "")
            .classes("w-full mt-3")
            .props("outlined dark color=amber")
        )
        with ui.row().classes("w-full gap-3 mt-3"):
            fsk_in = (
                ui.number("Altersfreigabe", value=film.altersfreigabe, min=0, max=18)
                .props("outlined dark color=amber")
                .classes("w-32")
            )
            preis_in = (
                ui.number("Preis (CHF)", value=float(film.basispreis), min=0, step=0.5, format="%.2f")
                .props("outlined dark color=amber")
                .classes("flex-1")
            )
        aktiv_toggle = ui.switch("Film aktiv", value=film.aktiv).classes("mt-3")

        err = ui.label("").classes("text-red-400 text-sm mt-2")

        def save() -> None:
            try:
                svc.admin_service().update_film(
                    account_id,
                    film.film_id,
                    {
                        "titel": titel_in.value.strip(),
                        "beschreibung": beschreibung_in.value.strip(),
                        "hauptdarsteller": hauptdarsteller_in.value.strip(),
                        "coverbild_url": coverbild_in.value.strip(),
                        "altersfreigabe": int(fsk_in.value or 0),
                        "basispreis": Decimal(str(preis_in.value or 0)),
                        "aktiv": aktiv_toggle.value,
                    },
                )
                ui.notify("Film gespeichert!", color="positive")
                dialog.close()
                on_done()
            except Exception as e:
                err.set_text(str(e))

        with ui.row().classes("justify-end gap-2 mt-4"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat color=gray")
            ui.button("Speichern", on_click=save).props("unelevated color=amber")

    dialog.open()


def _confirm_delete_film(film_id: UUID, film_titel: str, account_id: UUID | None, on_done) -> None:
    with ui.dialog() as dialog, ui.card().classes("bg-gray-800 min-w-80"):
        ui.label("Film löschen?").classes("text-xl font-bold text-red-400 mb-3")
        ui.label(f'"{film_titel}" wird unwiderruflich gelöscht.').classes("text-gray-300")

        def confirm() -> None:
            try:
                svc.admin_service().delete_film(account_id, film_id)
                ui.notify("Film gelöscht.", color="positive")
                dialog.close()
                on_done()
            except Exception as e:
                ui.notify(str(e), color="negative")
                dialog.close()

        with ui.row().classes("justify-end gap-2 mt-4"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat color=gray")
            ui.button("Löschen", on_click=confirm).props("unelevated color=red")

    dialog.open()


def _create_vorstellung_dialog(film_id: UUID, account_id: UUID | None, on_done) -> None:
    existing_saele = svc.get_existing_saele()
    existing_orte = svc.get_existing_orte()

    with ui.dialog() as dialog, ui.card().classes("bg-gray-800 min-w-96"):
        ui.label("Neue Vorstellung").classes("text-xl font-bold text-amber-400 mb-4")

        ort_in = ui.select(
            label="Ort",
            options=existing_orte or ["Zürich"],
            value=existing_orte[0] if existing_orte else "Zürich",
            with_input=True,
        ).classes("w-full").props("outlined dark color=amber")
        saal_in = ui.select(
            label="Saal",
            options=existing_saele or ["Saal 1"],
            value=existing_saele[0] if existing_saele else "Saal 1",
            with_input=True,
        ).classes("w-full mt-3").props("outlined dark color=amber")
        with ui.row().classes("w-full gap-3 mt-3"):
            start_date = (
                ui.date_input("Startdatum", value=date.today().strftime("%d.%m.%Y"))
                .props("outlined dark color=amber mask=##.##.####")
                .classes("flex-1")
            )
            _apply_german_date_picker(start_date)
        with ui.row().classes("w-full gap-3 mt-3"):
            start_time = (
                ui.input("Startzeit", value="19:30")
                .props("outlined dark color=amber type=time")
                .classes("w-36")
            )
            end_time = (
                ui.input("Endzeit", value="21:30")
                .props("outlined dark color=amber type=time")
                .classes("w-36")
            )

        err = ui.label("").classes("text-red-400 text-sm mt-2")

        def create() -> None:
            try:
                parsed_start = _parse_date(start_date.value)
                if not parsed_start:
                    err.set_text("Bitte Startdatum angeben.")
                    return
                start_time_obj = datetime.strptime(start_time.value or "19:30", "%H:%M").time()
                startzeit = datetime.combine(parsed_start, start_time_obj)
                end_time_obj = datetime.strptime(end_time.value or "21:30", "%H:%M").time()
                endzeit = datetime.combine(parsed_start, end_time_obj)
                if endzeit <= startzeit:
                    err.set_text("Endzeit muss nach der Startzeit liegen.")
                    return
                # Client-side conflict check: prüfe vorhandene Vorstellungen im gleichen Saal/Ort
                existing = svc.get_vorstellungen_in_saal_ort(saal_in.value.strip(), ort_in.value.strip())
                new_start = startzeit
                new_end = endzeit
                for ex in existing:
                    ex_start = ex["startzeit"]
                    ex_end = ex["endzeit"] or (ex_start + timedelta(hours=3))
                    if _overlaps(ex_start, ex_end, new_start, new_end):
                        err.set_text(f"Konflikt mit bestehender Vorstellung (Start: {ex_start}, Ende: {ex_end}) im {saal_in.value}.")
                        return

                svc.admin_service().create_vorstellung(
                    account_id=account_id,
                    film_id=film_id,
                    saal=saal_in.value.strip(),
                    ort=ort_in.value.strip(),
                    startzeit=startzeit,
                    endzeit=endzeit,
                )
                ui.notify("Vorstellung erstellt!", color="positive")
                dialog.close()
                on_done()
            except Exception as e:
                err.set_text(str(e))

        with ui.row().classes("justify-end gap-2 mt-4"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat color=gray")
            ui.button("Erstellen", on_click=create).props("unelevated color=amber")

    dialog.open()


def _edit_vorstellung_dialog(vorstellung_id: UUID, account_id: UUID | None, on_done) -> None:
    v = svc.film_service().get_vorstellung_by_id(vorstellung_id)
    if not v:
        ui.notify("Vorstellung nicht gefunden.", color="negative")
        return

    with ui.dialog() as dialog, ui.card().classes("bg-gray-800 min-w-96"):
        ui.label("Vorstellung bearbeiten").classes("text-xl font-bold text-amber-400 mb-4")

        existing_saele = svc.get_existing_saele()
        existing_orte = svc.get_existing_orte()

        ort_in = ui.select(
            label="Ort",
            options=sorted(set(existing_orte + ([v.ort] if v.ort else []))) or ["Zürich"],
            value=v.ort or (existing_orte[0] if existing_orte else "Zürich"),
            with_input=True,
        ).classes("w-full").props("outlined dark color=amber")
        saal_in = ui.select(
            label="Saal",
            options=sorted(set(existing_saele + ([v.saal] if v.saal else []))) or ["Saal 1"],
            value=v.saal or (existing_saele[0] if existing_saele else "Saal 1"),
            with_input=True,
        ).classes("w-full mt-3").props("outlined dark color=amber")
        start_date_val = v.startzeit.date() if v.startzeit else date.today()
        start_time_val = v.startzeit.strftime("%H:%M") if v.startzeit else "19:30"
        with ui.row().classes("w-full gap-3 mt-3"):
            start_date = (
                ui.date_input("Startdatum", value=start_date_val.strftime("%d.%m.%Y") if start_date_val else "")
                .props("outlined dark color=amber mask=##.##.####")
                .classes("flex-1")
            )
            _apply_german_date_picker(start_date)
            start_time = (
                ui.input("Startzeit", value=start_time_val)
                .props("outlined dark color=amber type=time")
                .classes("w-36")
            )
            end_time = ui.input("Endzeit", value=v.endzeit.strftime("%H:%M") if v.endzeit else "21:30").props(
                "outlined dark color=amber type=time"
            ).classes("w-36")

        err = ui.label("").classes("text-red-400 text-sm mt-2")

        def save() -> None:
            try:
                parsed_start = _parse_date(start_date.value)
                if not parsed_start:
                    err.set_text("Bitte Startdatum angeben.")
                    return
                start_time_obj = datetime.strptime(start_time.value or "19:30", "%H:%M").time()
                startzeit = datetime.combine(parsed_start, start_time_obj)
                end_time_obj = datetime.strptime(end_time.value or "21:30", "%H:%M").time()
                endzeit = datetime.combine(parsed_start, end_time_obj)
                if endzeit <= startzeit:
                    err.set_text("Endzeit muss nach der Startzeit liegen.")
                    return
                # Client-side conflict check for updates
                existing = svc.get_vorstellungen_in_saal_ort(saal_in.value.strip(), ort_in.value.strip())
                new_start = startzeit
                new_end = endzeit
                for ex in existing:
                    if ex["vorstellung_id"] == vorstellung_id:
                        continue
                    ex_start = ex["startzeit"]
                    ex_end = ex["endzeit"] or (ex_start + timedelta(hours=3))
                    if _overlaps(ex_start, ex_end, new_start, new_end):
                        err.set_text(f"Konflikt mit bestehender Vorstellung (Start: {ex_start}, Ende: {ex_end}) im {saal_in.value}.")
                        return

                svc.admin_service().update_vorstellung(
                    account_id=account_id,
                    vorstellung_id=vorstellung_id,
                    updates={"ort": ort_in.value.strip(), "saal": saal_in.value.strip(), "startzeit": startzeit, "endzeit": endzeit},
                )
                ui.notify("Vorstellung gespeichert!", color="positive")
                dialog.close()
                on_done()
            except Exception as e:
                err.set_text(str(e))

        with ui.row().classes("justify-end gap-2 mt-4"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat color=gray")
            ui.button("Speichern", on_click=save).props("unelevated color=amber")

    dialog.open()


def _confirm_delete_vorstellung(vorstellung_id: UUID, account_id: UUID | None, on_done) -> None:
    with ui.dialog() as dialog, ui.card().classes("bg-gray-800 min-w-72"):
        ui.label("Vorstellung löschen?").classes("text-xl font-bold text-red-400 mb-3")
        ui.label("Diese Aktion kann nicht rückgängig gemacht werden.").classes("text-gray-300 text-sm")

        def confirm() -> None:
            try:
                svc.admin_service().delete_vorstellung(account_id, vorstellung_id)
                ui.notify("Vorstellung gelöscht.", color="positive")
                dialog.close()
                on_done()
            except Exception as e:
                ui.notify(str(e), color="negative")
                dialog.close()

        with ui.row().classes("justify-end gap-2 mt-4"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat color=gray")
            ui.button("Löschen", on_click=confirm).props("unelevated color=red")

    dialog.open()
