from datetime import datetime
from decimal import Decimal
from uuid import UUID

from nicegui import ui

import frontend.services as svc
from frontend.auth import get_account_id, is_admin, is_logged_in
from frontend.components import navbar
from backend.models import Film


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
        all_films = svc.film_service().film_repo.list_all()
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
                    "erscheinungsdatum": str(f.erscheinungsdatum) if f.erscheinungsdatum else "–",
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
                        @click="$emit('edit', props.row)" />
                    <q-btn flat dense icon="delete" color="red"
                        @click="$emit('delete', props.row)" />
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

    all_films = svc.film_service().film_repo.list_all()
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

    all_films = svc.film_service().film_repo.list_all()
    film_options = {str(f.film_id): f.titel for f in all_films}

    film_sel = (
        ui.select(options=film_options, label="Film auswählen", with_input=True)
        .props("outlined dark color=amber")
        .classes("w-72")
    )

    result_area = ui.element("div").classes("w-full mt-4")

    def load_overview() -> None:
        if not film_sel.value:
            return
        try:
            overview = svc.admin_service().get_sales_overview(UUID(film_sel.value))
            result_area.clear()
            with result_area:
                with ui.row().classes("gap-4 flex-wrap mb-4"):
                    with ui.card().classes("bg-amber-800 rounded-xl p-4 text-center"):
                        ui.label(str(overview["verkaufte_tickets"])).classes("text-3xl font-bold text-white")
                        ui.label("Tickets verkauft").classes("text-amber-200 text-sm")
                    with ui.card().classes("bg-gray-700 rounded-xl p-4 text-center"):
                        ui.label(str(overview["freie_plaetze"])).classes("text-3xl font-bold text-white")
                        ui.label("Freie Plätze").classes("text-gray-300 text-sm")

                if overview["vorstellungen"]:
                    ui.label("Details pro Vorstellung").classes("text-lg font-bold text-white mt-4 mb-2")
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

    film_sel.on_value_change(lambda _: load_overview())


# --- Dialogs ---

def _create_film_dialog(account_id: UUID | None, on_done) -> None:
    kategorien = svc.get_all_kategorien()
    sprachen = svc.get_all_sprachen()

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

        ui.label("Erscheinungsdatum").classes("text-gray-400 text-sm mt-3")
        datum_in = ui.date().classes("w-full")

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
            from datetime import date as date_type
            from sqlmodel import Session, select as sql_select
            from backend.models.orm.kategorie_sql import Kategorie as KatORM
            from backend.models.orm.sprache_sql import Sprache as SprORM
            from config.database import engine

            try:
                raw_date = datum_in.value or ""
                erschein = date_type.fromisoformat(raw_date.replace("/", "-")) if raw_date else date_type.today()

                with Session(engine) as session:
                    kat_ids = [
                        session.exec(sql_select(KatORM).where(KatORM.name == n)).first().kategorie_id
                        for n in (kat_sel.value or [])
                        if session.exec(sql_select(KatORM).where(KatORM.name == n)).first()
                    ]
                    spr_ids = [
                        session.exec(sql_select(SprORM).where(SprORM.name == n)).first().sprache_id
                        for n in (spr_sel.value or [])
                        if session.exec(sql_select(SprORM).where(SprORM.name == n)).first()
                    ]

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
    with ui.dialog() as dialog, ui.card().classes("bg-gray-800 min-w-96"):
        ui.label("Neue Vorstellung").classes("text-xl font-bold text-amber-400 mb-4")

        ort_in = ui.input("Ort", value="Zürich").classes("w-full").props("outlined dark color=amber")
        saal_in = ui.input("Saal", value="Saal 1").classes("w-full mt-3").props("outlined dark color=amber")
        ui.label("Startzeit").classes("text-gray-400 text-sm mt-3")
        start_date = ui.date().classes("w-full")
        start_time = ui.time(value="19:30").classes("w-full mt-2")
        ui.label("Endzeit (optional)").classes("text-gray-400 text-sm mt-3")
        end_date = ui.date().classes("w-full")
        end_time = ui.time(value="21:30").classes("w-full mt-2")

        err = ui.label("").classes("text-red-400 text-sm mt-2")

        def create() -> None:
            try:
                raw_start = f"{(start_date.value or '').replace('/', '-')} {start_time.value or '19:30'}"
                startzeit = datetime.fromisoformat(raw_start)
                endzeit = None
                if end_date.value:
                    raw_end = f"{end_date.value.replace('/', '-')} {end_time.value or '21:30'}"
                    endzeit = datetime.fromisoformat(raw_end)
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
    v = svc.film_service().film_repo.get_vorstellung_by_id(vorstellung_id)
    if not v:
        ui.notify("Vorstellung nicht gefunden.", color="negative")
        return

    with ui.dialog() as dialog, ui.card().classes("bg-gray-800 min-w-96"):
        ui.label("Vorstellung bearbeiten").classes("text-xl font-bold text-amber-400 mb-4")

        ort_in = ui.input("Ort", value=v.ort or "").classes("w-full").props("outlined dark color=amber")
        saal_in = ui.input("Saal", value=v.saal or "").classes("w-full mt-3").props("outlined dark color=amber")
        ui.label("Startzeit").classes("text-gray-400 text-sm mt-3")
        start_date_val = v.startzeit.strftime("%Y/%m/%d") if v.startzeit else ""
        start_time_val = v.startzeit.strftime("%H:%M") if v.startzeit else "19:30"
        start_date = ui.date(value=start_date_val).classes("w-full")
        start_time = ui.time(value=start_time_val).classes("w-full mt-2")

        err = ui.label("").classes("text-red-400 text-sm mt-2")

        def save() -> None:
            try:
                raw_start = f"{(start_date.value or '').replace('/', '-')} {start_time.value or '19:30'}"
                startzeit = datetime.fromisoformat(raw_start)
                svc.admin_service().update_vorstellung(
                    account_id=account_id,
                    vorstellung_id=vorstellung_id,
                    updates={"ort": ort_in.value.strip(), "saal": saal_in.value.strip(), "startzeit": startzeit},
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
