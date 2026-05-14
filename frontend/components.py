from nicegui import ui

from frontend.auth import is_admin, is_logged_in, logout


def navbar() -> None:
    with ui.header().classes("bg-gray-900 border-b border-gray-700"):
        with ui.row().classes("w-full max-w-6xl mx-auto items-center justify-between px-4 h-16"):
            with ui.link(target="/").classes("no-underline"):
                ui.label("🎬 MoviTicket").classes("text-amber-400 text-xl font-bold")
            with ui.row().classes("items-center gap-6"):
                if is_logged_in():
                    ui.link("Filme", "/").classes("text-gray-300 hover:text-white text-sm no-underline")
                    if is_admin():
                        ui.link("Admin", "/admin").classes("text-gray-300 hover:text-white text-sm no-underline")
                    else:
                        ui.link("Mein Profil", "/profil").classes("text-gray-300 hover:text-white text-sm no-underline")
                    ui.button("Abmelden", on_click=logout).props("flat dense color=amber")
                else:
                    ui.link("Anmelden", "/login").classes("text-amber-400 hover:text-amber-300 text-sm no-underline")


def page_wrapper():
    return ui.column().classes("w-full max-w-6xl mx-auto px-4 py-8 min-h-screen")


def film_cover(coverbild_url: str | None, height: str = "h-48") -> None:
    url = coverbild_url or ""
    with ui.element("div").style(
        f"background-image: url('{url}'); "
        "background-size: cover; background-position: center; "
        f"width: 100%; background-color: #374151;"
    ).classes(height):
        pass
