from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from hashlib import sha256

from sqlmodel import Session, select

from backend.models.orm import (
    Account,
    Bestellung,
    Bewertung,
    FilmKategorie,
    FilmSprache,
    Film,
    FilmlisteKunde,
    Kategorie,
    Kunde,
    KundenKategoriePraeferenz,
    Sitzplatz,
    Snack,
    Sprache,
    TicketSnack,
    Ticket,
    Vorstellung,
    Zahlungsart,
)
from config.database import create_db_and_tables, engine

# Replace these placeholders with real fixture data as the project grows.
PAYMENT_METHODS = [
    {"name": "Kreditkarte"},
    {"name": "Twint"},
]

CATEGORIES = [
    {"name": "Action"},
    {"name": "Drama"},
    {"name": "Familie"},
]

LANGUAGES = [
    {"name": "Deutsch"},
    {"name": "Englisch"},
]

SNACKS = [
    {"name": "Popcorn klein", "preis": Decimal("6.50")},
    {"name": "Cola", "preis": Decimal("4.00")},
    {"name": "Nachos", "preis": Decimal("7.50")},
]

CUSTOMERS = [
    {
        "vorname": "Anna",
        "nachname": "Muster",
        "adresse": "Bahnhofstrasse 1",
        "plz": "8001",
        "geburtsdatum": date(1995, 4, 12),
        "telefonnummer": "+41 79 111 22 33",
        "email": "anna.muster@example.com",
        "passwort": "anna123",
        "zahlungsart_name": "Twint",
    },
    {
        "vorname": "Lukas",
        "nachname": "Beispiel",
        "adresse": "Hauptstrasse 42",
        "plz": "3000",
        "geburtsdatum": date(1988, 10, 3),
        "telefonnummer": "+41 79 444 55 66",
        "email": "lukas.beispiel@example.com",
        "passwort": "lukas123",
        "zahlungsart_name": "Kreditkarte",
    },
]

ADMIN_ACCOUNT = {
    "vorname": "System",
    "nachname": "Admin",
    "adresse": "",
    "plz": "",
    "geburtsdatum": date(1990, 1, 1),
    "telefonnummer": "",
    "email": "admin@example.com",
    "passwort": "admin123",
    "rolle": "admin",
}

FILMS = [
    {
        "titel": "Neon City",
        "beschreibung": "Actionfilm mit futuristischer Kulisse.",
        "altersfreigabe": 16,
        "coverbild_url": "https://example.com/covers/neon-city.jpg",
        "hauptdarsteller": "Mia Keller, Jonas Frei",
        "erscheinungsdatum": date(2026, 4, 1),
        "basispreis": Decimal("14.50"),
        "kategorien": ["Action"],
        "sprachen": ["Deutsch", "Englisch"],
    },
    {
        "titel": "Herzschlag",
        "beschreibung": "Emotionales Drama über Familie und Entscheidungen.",
        "altersfreigabe": 12,
        "coverbild_url": "https://example.com/covers/herzschlag.jpg",
        "hauptdarsteller": "Lena Baum, Tim Keller",
        "erscheinungsdatum": date(2026, 4, 15),
        "basispreis": Decimal("13.00"),
        "kategorien": ["Drama", "Familie"],
        "sprachen": ["Deutsch"],
    },
]


def seed_database() -> None:
    create_db_and_tables()

    with Session(engine) as session:
        _create_admin_account(session)

        zahlungsarten = _create_payment_methods(session)
        kategorien = _create_categories(session)
        sprachen = _create_languages(session)
        snacks = _create_snacks(session)
        kunden = _create_customers(session, zahlungsarten)
        filme = _create_films(session, kategorien, sprachen)
        vorstellungen, sitzplaetze = _create_vorstellungen_and_seats(session, filme)

        _create_association_rows(session, kunden, filme, kategorien, sprachen)
        bestellungen, tickets = _create_orders_and_tickets(session, kunden, filme, vorstellungen, sitzplaetze)
        _create_ticket_snacks(session, tickets, snacks)
        _create_ratings(session, kunden, filme)

        session.commit()


def _create_payment_methods(session: Session) -> list[Zahlungsart]:
    rows: list[Zahlungsart] = []
    for item in PAYMENT_METHODS:
        row = session.exec(select(Zahlungsart).where(Zahlungsart.name == item["name"])).first()
        if row is None:
            row = Zahlungsart(**item)
            session.add(row)
            session.flush()
        rows.append(row)
    return rows


def _create_categories(session: Session) -> list[Kategorie]:
    rows: list[Kategorie] = []
    for item in CATEGORIES:
        row = session.exec(select(Kategorie).where(Kategorie.name == item["name"])).first()
        if row is None:
            row = Kategorie(**item)
            session.add(row)
            session.flush()
        rows.append(row)
    return rows


def _create_languages(session: Session) -> list[Sprache]:
    rows: list[Sprache] = []
    for item in LANGUAGES:
        row = session.exec(select(Sprache).where(Sprache.name == item["name"])).first()
        if row is None:
            row = Sprache(**item)
            session.add(row)
            session.flush()
        rows.append(row)
    return rows


def _create_snacks(session: Session) -> list[Snack]:
    rows: list[Snack] = []
    for item in SNACKS:
        row = session.exec(select(Snack).where(Snack.name == item["name"])).first()
        if row is None:
            row = Snack(**item)
            session.add(row)
            session.flush()
        rows.append(row)
    return rows


def _create_admin_account(session: Session) -> Account:
    existing = session.exec(select(Account).where(Account.email == ADMIN_ACCOUNT["email"])).first()
    if existing is not None:
        return existing

    row = Account(
        email=ADMIN_ACCOUNT["email"],
        rolle=ADMIN_ACCOUNT["rolle"],
    )
    row.set_password(ADMIN_ACCOUNT["passwort"])
    session.add(row)
    session.flush()
    return row


def _create_customers(session: Session, zahlungsarten: list[Zahlungsart]) -> list[Kunde]:
    zahlungsart_map = {row.name: row for row in zahlungsarten}
    rows: list[Kunde] = []
    for item in CUSTOMERS:
        account = session.exec(select(Account).where(Account.email == item["email"])).first()
        if account is None:
            account = Account(email=item["email"], rolle="kunde")
            account.set_password(item["passwort"])
            session.add(account)
            session.flush()

        row = session.exec(select(Kunde).where(Kunde.account_id == account.account_id)).first()
        if row is None:
            row = Kunde(
                account_id=account.account_id,
                vorname=item["vorname"],
                nachname=item["nachname"],
                adresse=item["adresse"],
                plz=item["plz"],
                geburtsdatum=item["geburtsdatum"],
                telefonnummer=item["telefonnummer"],
                zahlungsart_id=zahlungsart_map[item["zahlungsart_name"]].zahlungsart_id,
            )
            session.add(row)
            session.flush()
        rows.append(row)
    return rows


def _create_films(
    session: Session,
    kategorien: list[Kategorie],
    sprachen: list[Sprache],
) -> list[Film]:
    kategorie_map = {row.name: row for row in kategorien}
    sprache_map = {row.name: row for row in sprachen}
    rows: list[Film] = []
    for item in FILMS:
        row = session.exec(select(Film).where(Film.titel == item["titel"])).first()
        if row is None:
            row = Film(
                titel=item["titel"],
                beschreibung=item["beschreibung"],
                altersfreigabe=item["altersfreigabe"],
                coverbild_url=item["coverbild_url"],
                hauptdarsteller=item["hauptdarsteller"],
                erscheinungsdatum=item["erscheinungsdatum"],
                basispreis=item["basispreis"],
                aktiv=True,
            )
            session.add(row)
            session.flush()
        rows.append(row)

    for film_row, item in zip(rows, FILMS, strict=False):
        for kategorie_name in item["kategorien"]:
            exists = session.exec(
                select(FilmKategorie).where(
                    FilmKategorie.film_id == film_row.film_id,
                    FilmKategorie.kategorie_id == kategorie_map[kategorie_name].kategorie_id,
                )
            ).first()
            if exists is None:
                session.add(FilmKategorie(film_id=film_row.film_id, kategorie_id=kategorie_map[kategorie_name].kategorie_id))
        for sprache_name in item["sprachen"]:
            exists = session.exec(
                select(FilmSprache).where(
                    FilmSprache.film_id == film_row.film_id,
                    FilmSprache.sprache_id == sprache_map[sprache_name].sprache_id,
                )
            ).first()
            if exists is None:
                session.add(FilmSprache(film_id=film_row.film_id, sprache_id=sprache_map[sprache_name].sprache_id))

    session.flush()
    return rows


def _create_vorstellungen_and_seats(
    session: Session,
    filme: list[Film],
) -> tuple[list[Vorstellung], list[Sitzplatz]]:
    vorstellungen: list[Vorstellung] = []
    sitzplaetze: list[Sitzplatz] = []

    for index, film in enumerate(filme, start=1):
        vorstellung = session.exec(
            select(Vorstellung).where(
                Vorstellung.film_id == film.film_id,
                Vorstellung.saal == f"Saal {index}",
                Vorstellung.ort == "Zürich",
            )
        ).first()
        if vorstellung is None:
            vorstellung = Vorstellung(
                film_id=film.film_id,
                saal=f"Saal {index}",
                ort="Zürich",
                startzeit=datetime(2026, 5, index, 19, 30),
                endzeit=datetime(2026, 5, index, 21, 45),
            )
            session.add(vorstellung)
            session.flush()
        vorstellungen.append(vorstellung)

    seat_plan = [("A1", "A"), ("A2", "A"), ("B1", "B"), ("B2", "B")]
    for vorstellung in vorstellungen:
        for label, sektor in seat_plan:
            seat_row = session.exec(
                select(Sitzplatz).where(
                    Sitzplatz.vorstellung_id == vorstellung.vorstellung_id,
                    Sitzplatz.sitz_label == label,
                )
            )
            seat_row = seat_row.first()
            if seat_row is None:
                seat_row = Sitzplatz(
                    vorstellung_id=vorstellung.vorstellung_id,
                    sitz_label=label,
                    sektor=sektor,
                    besetzt=False,
                )
                session.add(seat_row)
                session.flush()
            sitzplaetze.append(seat_row)
    return vorstellungen, sitzplaetze


def _create_association_rows(
    session: Session,
    kunden: list[Kunde],
    filme: list[Film],
    kategorien: list[Kategorie],
    sprachen: list[Sprache],
) -> None:
    items = [
        KundenKategoriePraeferenz(kunde_id=kunden[0].kunde_id, kategorie_id=kategorien[0].kategorie_id),
        KundenKategoriePraeferenz(kunde_id=kunden[1].kunde_id, kategorie_id=kategorien[1].kategorie_id),
        FilmlisteKunde(kunde_id=kunden[0].kunde_id, film_id=filme[1].film_id),
    ]
    for relation in items:
        if isinstance(relation, KundenKategoriePraeferenz):
            exists = session.exec(
                select(KundenKategoriePraeferenz).where(
                    KundenKategoriePraeferenz.kunde_id == relation.kunde_id,
                    KundenKategoriePraeferenz.kategorie_id == relation.kategorie_id,
                )
            ).first()
        else:
            exists = session.exec(
                select(FilmlisteKunde).where(
                    FilmlisteKunde.kunde_id == relation.kunde_id,
                    FilmlisteKunde.film_id == relation.film_id,
                )
            ).first()
        if exists is None:
            session.add(relation)


def _create_orders_and_tickets(
    session: Session,
    kunden: list[Kunde],
    filme: list[Film],
    vorstellungen: list[Vorstellung],
    sitzplaetze: list[Sitzplatz],
) -> tuple[list[Bestellung], list[Ticket]]:
    bestellungen: list[Bestellung] = []
    order_specs = [
        (kunden[0].kunde_id, datetime(2026, 4, 30, 10, 0), Decimal("20.50")),
        (kunden[1].kunde_id, datetime(2026, 4, 30, 11, 15), Decimal("17.00")),
    ]
    for kunde_id, bestellungsdatum, total_betrag in order_specs:
        bestellung = session.exec(
            select(Bestellung).where(
                Bestellung.kunde_id == kunde_id,
                Bestellung.bestellungsdatum == bestellungsdatum,
            )
        ).first()
        if bestellung is None:
            bestellung = Bestellung(
                kunde_id=kunde_id,
                bestellungsdatum=bestellungsdatum,
                anzahl_tickets=1,
                total_betrag=total_betrag,
            )
            session.add(bestellung)
            session.flush()
        bestellungen.append(bestellung)

    tickets = [
        Ticket(
            bestellung_id=bestellungen[0].bestellung_id,
            film_id=filme[0].film_id,
            vorstellung_id=vorstellungen[0].vorstellung_id,
            sitzplatz_id=sitzplaetze[0].sitzplatz_id,
            verguenstigungsart="regulaer",
            preis=Decimal("14.50"),
        ),
        Ticket(
            bestellung_id=bestellungen[1].bestellung_id,
            film_id=filme[1].film_id,
            vorstellung_id=vorstellungen[1].vorstellung_id,
            sitzplatz_id=sitzplaetze[4].sitzplatz_id,
            verguenstigungsart="student",
            preis=Decimal("10.40"),
        ),
    ]
    for ticket in tickets:
        exists = session.exec(select(Ticket).where(Ticket.ticket_id == ticket.ticket_id)).first()
        if exists is None:
            session.add(ticket)

    # Mark the seats as occupied so the seat state matches the demo tickets.
    sitzplaetze[0].besetzt = True
    sitzplaetze[4].besetzt = True
    session.add_all([sitzplaetze[0], sitzplaetze[4]])
    session.flush()
    return bestellungen, tickets


def _create_ticket_snacks(session: Session, tickets: list[Ticket], snacks: list[Snack]) -> None:
    rows = [
        TicketSnack(ticket_id=tickets[0].ticket_id, snack_id=snacks[0].snack_id, anzahl=1),
        TicketSnack(ticket_id=tickets[1].ticket_id, snack_id=snacks[1].snack_id, anzahl=2),
    ]
    for row in rows:
        exists = session.exec(
            select(TicketSnack).where(
                TicketSnack.ticket_id == row.ticket_id,
                TicketSnack.snack_id == row.snack_id,
            )
        ).first()
        if exists is None:
            session.add(row)


def _create_ratings(session: Session, kunden: list[Kunde], filme: list[Film]) -> None:
    rows = [
        Bewertung(
            kunde_id=kunden[0].kunde_id,
            film_id=filme[0].film_id,
            bewertung=5,
            kommentar="Starker Auftakt und gute Effekte.",
            bewertungsdatum=datetime(2026, 4, 30, 12, 0),
        ),
        Bewertung(
            kunde_id=kunden[1].kunde_id,
            film_id=filme[1].film_id,
            bewertung=4,
            kommentar="Emotional und gut gespielt.",
            bewertungsdatum=datetime(2026, 4, 30, 12, 30),
        ),
    ]
    for row in rows:
        exists = session.exec(
            select(Bewertung).where(
                Bewertung.kunde_id == row.kunde_id,
                Bewertung.film_id == row.film_id,
                Bewertung.bewertungsdatum == row.bewertungsdatum,
            )
        ).first()
        if exists is None:
            session.add(row)
