from uuid import UUID

_svc: dict = {}


def init_services(user_service, film_service, bestellung_service, admin_service, lookup_service, snack_service) -> None:
    _svc.update({
        "user": user_service,
        "film": film_service,
        "bestellung": bestellung_service,
        "admin": admin_service,
        "lookup": lookup_service,
        "snack": snack_service,
    })


def user_service():
    return _svc["user"]


def film_service():
    return _svc["film"]


def bestellung_service():
    return _svc["bestellung"]


def admin_service():
    return _svc["admin"]


def lookup_service():
    return _svc["lookup"]


def snack_service():
    return _svc["snack"]


def get_all_kategorien() -> list[dict]:
    return lookup_service().list_categories()


def get_all_sprachen() -> list[dict]:
    return lookup_service().list_languages()


def get_all_zahlungsarten() -> list[dict]:
    return lookup_service().list_payment_methods()


def get_kategorie_names(ids: list[UUID]) -> list[str]:
    return lookup_service().get_category_names(ids)


def get_all_seats_for_vorstellung(vorstellung_id: UUID) -> list[dict]:
    return lookup_service().get_all_seats_for_vorstellung(vorstellung_id)


def get_vorstellungen_in_saal_ort(saal: str, ort: str) -> list[dict]:
    return lookup_service().get_vorstellungen_in_saal_ort(saal, ort)


def get_existing_saele() -> list[str]:
    return lookup_service().get_existing_saele()


def get_existing_orte() -> list[str]:
    return lookup_service().get_existing_orte()


def get_sitzplatz_info(sitzplatz_id: UUID) -> dict | None:
    return lookup_service().get_sitzplatz_info(sitzplatz_id)


def get_sprache_names(ids: list[UUID]) -> list[str]:
    return lookup_service().get_language_names(ids)
