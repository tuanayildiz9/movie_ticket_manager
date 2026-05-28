from backend.repositories import (
    AccountRepository,
    BestellungRepository,
    BewertungRepository,
    FilmRepository,
    KundeRepository,
    SnackRepository,
)
from backend.services import AdminService, BestellungService, FilmService, LookupService, SnackService, UserService
from backend.seed import seed_database


def build_application():
    seed_database()

    account_repo = AccountRepository()
    kunde_repo = KundeRepository()
    film_repo = FilmRepository()
    bestellung_repo = BestellungRepository()
    bewertung_repo = BewertungRepository()
    snack_repo = SnackRepository()
    lookup_service = LookupService()

    film_service = FilmService(film_repo=film_repo, bewertung_repo=bewertung_repo, kunde_repo=kunde_repo)
    user_service = UserService(account_repo=account_repo, kunde_repo=kunde_repo)
    bestellung_service = BestellungService(
        bestellung_repo=bestellung_repo,
        film_repo=film_repo,
        kunde_repo=kunde_repo,
        snack_repo=snack_repo,
    )
    admin_service = AdminService(film_repo=film_repo, bestellung_repo=bestellung_repo, account_repo=account_repo)
    snack_service = SnackService(snack_repo=snack_repo)

    return user_service, film_service, bestellung_service, admin_service, lookup_service, snack_service


if __name__ in {"__main__", "__mp_main__"}:
    from nicegui import ui

    import frontend.services as svc_container
    import frontend.pages  # noqa: F401 – registers all @ui.page routes

    user_svc, film_svc, bestellung_svc, admin_svc, lookup_svc, snack_svc = build_application()
    svc_container.init_services(user_svc, film_svc, bestellung_svc, admin_svc, lookup_svc, snack_svc)

    ui.run(
        title="MovieTicket",
        port=8080,
        dark=True,
        storage_secret="movticket-secret-2024",
        favicon="🎬",
    )
