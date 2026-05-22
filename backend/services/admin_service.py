from datetime import datetime
from uuid import UUID

from sqlmodel import Session, select

from backend.models import Film
from backend.models.orm.sitzplatz_sql import Sitzplatz as SitzplatzORM
from backend.models.orm.vorstellung_sql import Vorstellung as VorstellungORM
from backend.repositories.account_repository import AccountRepository
from backend.repositories.bestellung_repository import BestellungRepository
from backend.repositories.film_repository import FilmRepository
from config.database import engine


class AdminService:
    def __init__(self, film_repo: FilmRepository, bestellung_repo: BestellungRepository, account_repo: AccountRepository | None = None) -> None:
        self.film_repo = film_repo
        self.bestellung_repo = bestellung_repo
        self.account_repo = account_repo
        # no custom exceptions here; use standard exceptions

    def _require_admin(self, account_id: UUID) -> None:
        if self.account_repo is None:
            raise RuntimeError("AccountRepository not configured for admin checks.")
        account = self.account_repo.get_by_id(account_id)
        if account is None:
            raise ValueError("Account wurde nicht gefunden.")
        if account.rolle != "admin":
            raise PermissionError("Nicht berechtigt: Admin-Rechte erforderlich.")

    def get_ticket_sales(self, film_id: UUID) -> int:
        return sum(len(bestellung.tickets) for bestellung in self.bestellung_repo.list_by_film(film_id))

    def get_free_seats(self, film_id: UUID) -> int:
        return sum(vorstellung.free_seat_count() for vorstellung in self.film_repo.list_vorstellungen_by_film(film_id))

    def get_sales_overview(self, film_id: UUID) -> dict[str, object]:
        film = self.film_repo.get_by_id(film_id)
        if film is None:
            raise ValueError("Film wurde nicht gefunden.")

        vorstellungen = [
            {
                "vorstellung_id": vorstellung.vorstellung_id,
                "saal": vorstellung.saal,
                "ort": vorstellung.ort,
                "startzeit": vorstellung.startzeit,
                "verkaufte_tickets": vorstellung.sold_ticket_count(),
                "freie_plaetze": vorstellung.free_seat_count(),
            }
            for vorstellung in film.vorstellungen
        ]

        return {
            "film_id": film_id,
            "titel": film.titel,
            "verkaufte_tickets": self.get_ticket_sales(film_id),
            "freie_plaetze": self.get_free_seats(film_id),
            "vorstellungen": vorstellungen,
        }

    # --- Admin CRUD for films ---
    def create_film(self, account_id: UUID, film: Film) -> Film:
        self._require_admin(account_id)
        return self.film_repo.save(film)

    def update_film(self, account_id: UUID, film_id: UUID, updates: dict) -> Film:
        self._require_admin(account_id)
        return self.film_repo.update_metadata(film_id, updates)

    def delete_film(self, account_id: UUID, film_id: UUID) -> None:
        self._require_admin(account_id)
        now = datetime.utcnow()

        future_vorstellungen = [
            vorstellung
            for vorstellung in self.film_repo.list_vorstellungen_by_film(film_id)
            if vorstellung.startzeit and vorstellung.startzeit > now
        ]
        if future_vorstellungen:
            raise ValueError("Film kann nicht gelöscht werden: Es gibt noch zukünftige Vorstellungen.")

        if self.bestellung_repo.has_future_tickets_by_film(film_id, now):
            raise ValueError("Film kann nicht gelöscht werden: Es gibt noch Tickets für zukünftige Vorstellungen.")

        self.film_repo.delete(film_id)

    # --- Admin CRUD for vorstellungen (showtimes) ---
    def create_vorstellung(self, account_id: UUID, film_id: UUID, saal: str, ort: str, startzeit, endzeit=None):
        self._require_admin(account_id)
        with Session(engine) as session:
            row = VorstellungORM(film_id=film_id, saal=saal, ort=ort, startzeit=startzeit, endzeit=endzeit)
            session.add(row)
            session.commit()
            session.refresh(row)
            return self.film_repo.get_vorstellung_by_id(row.vorstellung_id)

    def update_vorstellung(self, account_id: UUID, vorstellung_id: UUID, updates: dict):
        self._require_admin(account_id)
        with Session(engine) as session:
            row = session.get(VorstellungORM, vorstellung_id)
            if row is None:
                raise ValueError("Vorstellung wurde nicht gefunden.")
            for key in ["saal", "ort", "startzeit", "endzeit"]:
                if key in updates:
                    setattr(row, key, updates[key])
            session.add(row)
            session.commit()
            return self.film_repo.get_vorstellung_by_id(vorstellung_id)

    def delete_vorstellung(self, account_id: UUID, vorstellung_id: UUID) -> None:
        self._require_admin(account_id)
        with Session(engine) as session:
            row = session.get(VorstellungORM, vorstellung_id)
            if row is None:
                return
            if row.startzeit and row.startzeit > datetime.utcnow():
                orders = self.bestellung_repo.list_by_vorstellung(vorstellung_id)
                if orders:
                    raise ValueError("Vorstellung kann nicht gelöscht werden: Es gibt bereits Tickets für eine zukünftige Vorstellung.")

            self.bestellung_repo.delete_tickets_by_vorstellung(vorstellung_id)

            for seat in session.exec(select(SitzplatzORM).where(SitzplatzORM.vorstellung_id == vorstellung_id)).all():
                session.delete(seat)
            session.delete(row)
            session.commit()
