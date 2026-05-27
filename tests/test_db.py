from decimal import Decimal
from uuid import uuid4

from backend.models import Bestellung, Ticket, Verguensigungsart
from backend.repositories import BestellungRepository, FilmRepository


def test_film_query_returns_seeded_films(seeded_db):
    film_repo, film1, film2 = seeded_db
    films = film_repo.list_all()
    assert len(films) == 2
    titles = {f.titel for f in films}
    assert "Inception" in titles
    assert "Matrix" in titles


def test_saving_bestellung_persists_with_tickets(seeded_db, bestellung_repo):
    film_repo, film1, film2 = seeded_db
    vorstellung = film1.vorstellungen[0]
    sitzplatz = vorstellung.sitzplaetze[0]

    ticket = Ticket(
        film_id=film1.film_id,
        vorstellung_id=vorstellung.vorstellung_id,
        sitzplatz_id=sitzplatz.sitzplatz_id,
        verguenstigungsart=Verguensigungsart.REGULAER,
    )
    ticket.apply_discount(film1.basispreis)

    bestellung = Bestellung(kunde_id=uuid4())
    bestellung.add_ticket(ticket)
    bestellung.calculate_total()

    saved = bestellung_repo.create(bestellung)
    loaded = bestellung_repo.get_by_id(saved.bestellung_id)

    assert loaded is not None
    assert len(loaded.tickets) == 1
    assert loaded.total_betrag == Decimal("18.00")


def test_empty_db_returns_no_films(test_engine):
    film_repo = FilmRepository()
    assert film_repo.list_all() == []
