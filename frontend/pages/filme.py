from nicegui import ui

import frontend.services as svc
from frontend.auth import is_logged_in
from frontend.components import film_cover, navbar


@ui.page("/")
def filme_page() -> None:
    if not is_logged_in():
        ui.navigate.to("/login")
        return

    navbar()

    kategorien = svc.get_all_kategorien()
    sprachen = svc.get_all_sprachen()
    kat_options = {"": "Alle Kategorien"} | {k["name"]: k["name"] for k in kategorien}
    spr_options = {"": "Alle Sprachen"} | {s["name"]: s["name"] for s in sprachen}
    sort_options = {
        "titel": "Name (A–Z)",
        "-titel": "Name (Z–A)",
        "basispreis": "Preis aufsteigend",
        "-basispreis": "Preis absteigend",
        "-erscheinungsdatum": "Neu zuerst",
    }

    with ui.column().classes("w-full max-w-6xl mx-auto px-4 py-8"):
        ui.label("Aktuelle Filme").classes("text-3xl font-bold text-white mb-6")

        with ui.row().classes("w-full gap-3 flex-wrap mb-6 items-end"):
            search_in = (
                ui.input(placeholder="Film suchen …")
                .props("outlined dark color=amber clearable")
                .classes("flex-1 min-w-48")
            )
            kat_sel = (
                ui.select(options=kat_options, value=[], label="Kategorien", multiple=True)
                .props("outlined dark color=amber")
                .classes("w-64")
            )
            spr_sel = (
                ui.select(options=spr_options, value=[], label="Sprachen", multiple=True)
                .props("outlined dark color=amber")
                .classes("w-56")
            )
            sort_sel = (
                ui.select(options=sort_options, value="titel", label="Sortierung")
                .props("outlined dark color=amber")
                .classes("w-52")
            )
            ui.button("Zurücksetzen", icon="clear", on_click=lambda: reset_filters()).props("flat color=amber")

        films_container = ui.element("div").classes("w-full")

        def load_films() -> None:
            kat_values = kat_sel.value or []
            spr_values = spr_sel.value or []
            films = svc.film_service().search_films(
                search_term=search_in.value or None,
                kategorie_name=kat_values or None,
                sprache_name=spr_values or None,
                only_active=True,
                sort=sort_sel.value,
                size=60,
            )
            films_container.clear()
            with films_container:
                if not films:
                    with ui.column().classes("w-full items-center py-16"):
                        ui.icon("movie_filter", size="4rem").classes("text-gray-600")
                        ui.label("Keine Filme gefunden.").classes("text-gray-500 mt-3")
                    return
                with ui.grid().classes("w-full gap-5").style(
                    "grid-template-columns: repeat(auto-fill, minmax(200px, 1fr))"
                ):
                    for film in films:
                        kat_names = svc.get_kategorie_names(film.kategorie_ids)
                        film_id_str = str(film.film_id)
                        with (
                            ui.card()
                            .classes(
                                "bg-gray-800 rounded-xl overflow-hidden cursor-pointer "
                                "hover:ring-2 hover:ring-amber-400 transition-all p-0"
                            )
                            .on("click", lambda fid=film_id_str: ui.navigate.to(f"/film/{fid}"))
                        ):
                            film_cover(film.coverbild_url, "h-48")
                            with ui.column().classes("p-3 gap-1"):
                                ui.label(film.titel).classes("text-white font-bold text-sm leading-tight")
                                with ui.row().classes("items-center gap-1 flex-wrap mt-1"):
                                    ui.badge(f"FSK {film.altersfreigabe}").props("color=amber")
                                    for kat in kat_names:
                                        ui.badge(kat).props("color=blue-grey outline")
                                ui.label(f"ab CHF {film.basispreis:.2f}").classes(
                                    "text-amber-400 text-sm font-semibold mt-1"
                                )

        def reset_filters() -> None:
            search_in.set_value("")
            kat_sel.set_value([])
            spr_sel.set_value([])
            sort_sel.set_value("titel")
            load_films()

        # Live-Filter: bei jeder Änderung sofort neu laden
        search_in.on_value_change(lambda _: load_films())
        kat_sel.on("update:model-value", lambda _: load_films())
        spr_sel.on("update:model-value", lambda _: load_films())
        sort_sel.on("update:model-value", lambda _: load_films())

        load_films()
