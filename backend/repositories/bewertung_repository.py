from datetime import datetime
from uuid import UUID

from sqlmodel import Session, select

from backend.models import Bewertung
from backend.models.orm.bewertung_sql import Bewertung as BewertungORM
from config.database import engine

class BewertungRepository:
    def _to_domain(self, row: BewertungORM) -> Bewertung:
        return Bewertung(
            bewertung_id=row.bewertung_id,
            kunde_id=row.kunde_id,
            film_id=row.film_id,
            bewertung=row.bewertung,
            kommentar=row.kommentar,
            bewertungsdatum=row.bewertungsdatum or datetime.utcnow(),
        )

    def create(self, bewertung: Bewertung) -> Bewertung:
        with Session(engine) as session:
            row = BewertungORM(
                bewertung_id=bewertung.bewertung_id,
                kunde_id=bewertung.kunde_id,
                film_id=bewertung.film_id,
                bewertung=bewertung.bewertung,
                kommentar=bewertung.kommentar,
                bewertungsdatum=bewertung.bewertungsdatum,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return self._to_domain(row)

    def list_by_film(self, film_id: UUID) -> list[Bewertung]:
        with Session(engine) as session:
            rows = session.exec(select(BewertungORM).where(BewertungORM.film_id == film_id)).all()
            return [self._to_domain(row) for row in rows]

    def list_by_kunde(self, kunde_id: UUID) -> list[Bewertung]:
        with Session(engine) as session:
            rows = session.exec(select(BewertungORM).where(BewertungORM.kunde_id == kunde_id)).all()
            return [self._to_domain(row) for row in rows]

    def list_all(self) -> list[Bewertung]:
        with Session(engine) as session:
            rows = session.exec(select(BewertungORM)).all()
            return [self._to_domain(row) for row in rows]
