from decimal import Decimal

import pytest

from backend.models import Verguensigungsart
from backend.repositories import (
    BestellungRepository,
    FilmRepository,
    KundeRepository,
    SnackRepository,
)
from backend.services.bestellung_service import BestellungService


def _make_service() -> BestellungService:
    return BestellungService(
        bestellung_repo=BestellungRepository(),
        film_repo=FilmRepository(),
        kunde_repo=KundeRepository(),
        snack_repo=SnackRepository(),
    )


def test_create_order_single_ticket(seeded_db, seeded_kunde):
    film_repo, film1, film2 = seeded_db
    service = _make_service()
    vorstellung = film1.vorstellungen[0]
    sitzplatz = vorstellung.sitzplaetze[0]

    bestellung = service.create_order(
        kunde_id=seeded_kunde.kunde_id,
        tickets=[{
            "film_id": film1.film_id,
            "vorstellung_id": vorstellung.vorstellung_id,
            "sitzplatz_id": sitzplatz.sitzplatz_id,
            "verguenstigungsart": Verguensigungsart.REGULAER,
        }],
    )

    assert bestellung.bestellung_id is not None
    assert bestellung.anzahl_tickets == 1
    assert bestellung.total_betrag == Decimal("18.00")


def test_create_order_student_discount_applied(seeded_db, seeded_kunde):
    film_repo, film1, film2 = seeded_db
    service = _make_service()
    vorstellung = film1.vorstellungen[0]
    sitzplaetze = vorstellung.sitzplaetze

    bestellung = service.create_order(
        kunde_id=seeded_kunde.kunde_id,
        tickets=[
            {
                "film_id": film1.film_id,
                "vorstellung_id": vorstellung.vorstellung_id,
                "sitzplatz_id": sitzplaetze[0].sitzplatz_id,
                "verguenstigungsart": Verguensigungsart.STUDENT,
            },
            {
                "film_id": film1.film_id,
                "vorstellung_id": vorstellung.vorstellung_id,
                "sitzplatz_id": sitzplaetze[1].sitzplatz_id,
                "verguenstigungsart": Verguensigungsart.REGULAER,
            },
        ],
    )

    # Inception base = 18.00 CHF
    # Ticket 1 (student):  18 - 4 = 14.00
    # Ticket 2 (regular):  18 - 0 = 18.00
    assert bestellung.anzahl_tickets == 2
    assert bestellung.total_betrag == Decimal("32.00")


def test_kind_discount_blocked_for_adult_film(seeded_db, seeded_kunde):
    film_repo, film1, film2 = seeded_db  # film2 has altersfreigabe=16
    service = _make_service()
    vorstellung = film2.vorstellungen[0]
    sitzplatz = vorstellung.sitzplaetze[0]

    with pytest.raises(ValueError, match="Kindervergünstigung"):
        service.create_order(
            kunde_id=seeded_kunde.kunde_id,
            tickets=[{
                "film_id": film2.film_id,
                "vorstellung_id": vorstellung.vorstellung_id,
                "sitzplatz_id": sitzplatz.sitzplatz_id,
                "verguenstigungsart": Verguensigungsart.KIND,
            }],
        )
