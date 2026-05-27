import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlmodel import SQLModel, create_engine

import backend.models.orm  # noqa – registers all ORM tables with SQLModel.metadata


@pytest.fixture(scope="function")
def test_engine(monkeypatch):
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    import backend.repositories.film_repository as _film
    import backend.repositories.bestellung_repository as _best
    import backend.repositories.kunde_repository as _kunde
    import backend.repositories.snack_repository as _snack
    import backend.repositories.account_repository as _acct
    import backend.repositories.bewertung_repository as _bew

    monkeypatch.setattr(_film, "engine", engine)
    monkeypatch.setattr(_best, "engine", engine)
    monkeypatch.setattr(_kunde, "engine", engine)
    monkeypatch.setattr(_snack, "engine", engine)
    monkeypatch.setattr(_acct, "engine", engine)
    monkeypatch.setattr(_bew, "engine", engine)

    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def film_repo(test_engine):
    from backend.repositories import FilmRepository
    return FilmRepository()


@pytest.fixture
def bestellung_repo(test_engine):
    from backend.repositories import BestellungRepository
    return BestellungRepository()


@pytest.fixture
def kunde_repo(test_engine):
    from backend.repositories import KundeRepository
    return KundeRepository()


@pytest.fixture
def snack_repo(test_engine):
    from backend.repositories import SnackRepository
    return SnackRepository()


@pytest.fixture
def seeded_db(film_repo, test_engine):
    from backend.models import Film, Vorstellung, Sitzplatz

    v1_id = uuid4()
    film1 = Film(
        titel="Inception",
        basispreis=Decimal("18.00"),
        altersfreigabe=12,
        erscheinungsdatum=date.today(),
        aktiv=True,
    )
    v1 = Vorstellung(
        vorstellung_id=v1_id,
        film_id=film1.film_id,
        saal="Saal 1",
        ort="Bern",
        startzeit=datetime.utcnow() + timedelta(days=1),
        sitzplaetze=[
            Sitzplatz(sitz_label="A1", sektor="A", vorstellung_id=v1_id),
            Sitzplatz(sitz_label="A2", sektor="A", vorstellung_id=v1_id),
        ],
    )
    film1.vorstellungen.append(v1)

    v2_id = uuid4()
    film2 = Film(
        titel="Matrix",
        basispreis=Decimal("20.00"),
        altersfreigabe=16,
        erscheinungsdatum=date.today(),
        aktiv=True,
    )
    v2 = Vorstellung(
        vorstellung_id=v2_id,
        film_id=film2.film_id,
        saal="Saal 2",
        ort="Bern",
        startzeit=datetime.utcnow() + timedelta(days=2),
        sitzplaetze=[
            Sitzplatz(sitz_label="B1", sektor="B", vorstellung_id=v2_id),
        ],
    )
    film2.vorstellungen.append(v2)

    saved1 = film_repo.save(film1)
    saved2 = film_repo.save(film2)
    return film_repo, saved1, saved2


@pytest.fixture
def seeded_kunde(kunde_repo):
    from backend.models import Kunde
    kunde = Kunde(
        vorname="Max",
        nachname="Mustermann",
        geburtsdatum=date(1990, 1, 1),
        adresse="Teststrasse 1",
        plz="3000",
        ort="Bern",
    )
    return kunde_repo.create(kunde)
