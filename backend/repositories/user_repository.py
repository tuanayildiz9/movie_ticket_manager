from datetime import date
from uuid import UUID

from sqlmodel import Session, select

from backend.models import Kunde, Zahlungsart
from backend.models.orm.filmliste_kunde_sql import FilmlisteKunde
from backend.models.orm.kunde_sql import Kunde as KundeORM
from backend.models.orm.kunden_kategorie_praeferenz_sql import KundenKategoriePraeferenz
from backend.models.orm.zahlungsart_sql import Zahlungsart as ZahlungsartORM
from config.database import engine

from .user_repository_interface import IUserRepository


class UserRepository(IUserRepository):
    def _to_domain(self, session: Session, row: KundeORM) -> Kunde:
        zahlungsart = None
        if row.zahlungsart_id is not None:
            payment_row = session.get(ZahlungsartORM, row.zahlungsart_id)
            if payment_row is not None:
                zahlungsart = Zahlungsart(zahlungsart_id=payment_row.zahlungsart_id, name=payment_row.name)

        gespeicherte_filme = [
            link.film_id
            for link in session.exec(select(FilmlisteKunde).where(FilmlisteKunde.kunde_id == row.kunde_id)).all()
        ]
        kategorien_praeferenzen = [
            link.kategorie_id
            for link in session.exec(
                select(KundenKategoriePraeferenz).where(KundenKategoriePraeferenz.kunde_id == row.kunde_id)
            ).all()
        ]

        return Kunde(
            kunde_id=row.kunde_id,
            vorname=row.vorname,
            nachname=row.nachname,
            adresse=row.adresse,
            plz=row.plz,
            geburtsdatum=row.geburtsdatum,
            telefonnummer=row.telefonnummer,
            email=row.email,
            passwort_hash=row.passwort_hash,
            zahlungsart=zahlungsart,
            gespeicherte_filme=gespeicherte_filme,
            kategorien_praeferenzen=kategorien_praeferenzen,
        )

    def _ensure_payment_type(self, session: Session, zahlungsart: Zahlungsart | None) -> UUID | None:
        if zahlungsart is None:
            return None

        row = session.get(ZahlungsartORM, zahlungsart.zahlungsart_id)
        if row is None:
            row = session.exec(select(ZahlungsartORM).where(ZahlungsartORM.name == zahlungsart.name)).first()
        if row is None:
            row = ZahlungsartORM(zahlungsart_id=zahlungsart.zahlungsart_id, name=zahlungsart.name)
            session.add(row)
            session.flush()
        return row.zahlungsart_id

    def _sync_preferences(self, session: Session, kunde: Kunde) -> None:
        session.exec(
            select(FilmlisteKunde).where(FilmlisteKunde.kunde_id == kunde.kunde_id)
        ).all()
        for link in session.exec(select(FilmlisteKunde).where(FilmlisteKunde.kunde_id == kunde.kunde_id)).all():
            session.delete(link)
        for link in session.exec(
            select(KundenKategoriePraeferenz).where(KundenKategoriePraeferenz.kunde_id == kunde.kunde_id)
        ).all():
            session.delete(link)

        for film_id in kunde.gespeicherte_filme:
            session.add(FilmlisteKunde(kunde_id=kunde.kunde_id, film_id=film_id))
        for kategorie_id in kunde.kategorien_praeferenzen:
            session.add(KundenKategoriePraeferenz(kunde_id=kunde.kunde_id, kategorie_id=kategorie_id))

    def create(self, kunde: Kunde) -> Kunde:
        with Session(engine) as session:
            zahlungsart_id = self._ensure_payment_type(session, kunde.zahlungsart)
            row = KundeORM(
                kunde_id=kunde.kunde_id,
                vorname=kunde.vorname,
                nachname=kunde.nachname,
                adresse=kunde.adresse,
                plz=kunde.plz,
                geburtsdatum=kunde.geburtsdatum,
                telefonnummer=kunde.telefonnummer,
                email=kunde.email,
                passwort_hash=kunde.passwort_hash,
                zahlungsart_id=zahlungsart_id,
            )
            session.add(row)
            session.flush()
            self._sync_preferences(session, kunde)
            session.commit()
            session.refresh(row)
            return self._to_domain(session, row)

    def get_by_id(self, kunde_id: UUID) -> Kunde | None:
        with Session(engine) as session:
            row = session.get(KundeORM, kunde_id)
            return self._to_domain(session, row) if row else None

    def get_by_email(self, email: str) -> Kunde | None:
        with Session(engine) as session:
            row = session.exec(select(KundeORM).where(KundeORM.email == email.lower())).first()
            return self._to_domain(session, row) if row else None

    def update(self, kunde: Kunde) -> Kunde:
        with Session(engine) as session:
            row = session.get(KundeORM, kunde.kunde_id)
            if row is None:
                return self.create(kunde)

            row.vorname = kunde.vorname
            row.nachname = kunde.nachname
            row.adresse = kunde.adresse
            row.plz = kunde.plz
            row.geburtsdatum = kunde.geburtsdatum
            row.telefonnummer = kunde.telefonnummer
            row.email = kunde.email
            row.passwort_hash = kunde.passwort_hash
            row.zahlungsart_id = self._ensure_payment_type(session, kunde.zahlungsart)

            for link in session.exec(select(FilmlisteKunde).where(FilmlisteKunde.kunde_id == kunde.kunde_id)).all():
                session.delete(link)
            for link in session.exec(
                select(KundenKategoriePraeferenz).where(KundenKategoriePraeferenz.kunde_id == kunde.kunde_id)
            ).all():
                session.delete(link)

            for film_id in kunde.gespeicherte_filme:
                session.add(FilmlisteKunde(kunde_id=kunde.kunde_id, film_id=film_id))
            for kategorie_id in kunde.kategorien_praeferenzen:
                session.add(KundenKategoriePraeferenz(kunde_id=kunde.kunde_id, kategorie_id=kategorie_id))

            session.add(row)
            session.commit()
            session.refresh(row)
            return self._to_domain(session, row)

    def delete(self, kunde_id: UUID) -> None:
        with Session(engine) as session:
            row = session.get(KundeORM, kunde_id)
            if row is None:
                return
            for link in session.exec(select(FilmlisteKunde).where(FilmlisteKunde.kunde_id == kunde_id)).all():
                session.delete(link)
            for link in session.exec(select(KundenKategoriePraeferenz).where(KundenKategoriePraeferenz.kunde_id == kunde_id)).all():
                session.delete(link)
            session.delete(row)
            session.commit()

    def list_all(self) -> list[Kunde]:
        with Session(engine) as session:
            rows = session.exec(select(KundeORM)).all()
            return [self._to_domain(session, row) for row in rows]

