from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlmodel import Session, delete, select

from backend.models import Film, Sitzplatz, Vorstellung
from backend.models.orm.film_kategorie_sql import FilmKategorie
from backend.models.orm.film_sprache_sql import FilmSprache
from backend.models.orm.film_sql import Film as FilmORM
from backend.models.orm.filmliste_kunde_sql import FilmlisteKunde
from backend.models.orm.kategorie_sql import Kategorie
from backend.models.orm.sitzplatz_sql import Sitzplatz as SitzplatzORM
from backend.models.orm.sprache_sql import Sprache
from backend.models.orm.vorstellung_sql import Vorstellung as VorstellungORM
from config.database import engine

class FilmRepository:
    def _to_domain(self, session: Session, row: FilmORM) -> Film:
        film = Film(
            film_id=row.film_id,
            titel=row.titel,
            beschreibung=row.beschreibung,
            altersfreigabe=row.altersfreigabe,
            coverbild_url=row.coverbild_url,
            hauptdarsteller=row.hauptdarsteller,
            erscheinungsdatum=row.erscheinungsdatum,
            basispreis=row.basispreis,
            aktiv=row.aktiv,
        )
        film.sprache_ids = [link.sprache_id for link in session.exec(select(FilmSprache).where(FilmSprache.film_id == row.film_id)).all()]
        film.kategorie_ids = [link.kategorie_id for link in session.exec(select(FilmKategorie).where(FilmKategorie.film_id == row.film_id)).all()]

        vorstellungen = session.exec(select(VorstellungORM).where(VorstellungORM.film_id == row.film_id)).all()
        for vorstellung_row in vorstellungen:
            sitzplaetze = session.exec(select(SitzplatzORM).where(SitzplatzORM.vorstellung_id == vorstellung_row.vorstellung_id)).all()
            vorstellung = Vorstellung(
                vorstellung_id=vorstellung_row.vorstellung_id,
                film_id=vorstellung_row.film_id,
                saal=vorstellung_row.saal,
                ort=vorstellung_row.ort,
                startzeit=vorstellung_row.startzeit,
                endzeit=vorstellung_row.endzeit,
                sitzplaetze=[
                    Sitzplatz(
                        sitzplatz_id=seat.sitzplatz_id,
                        sitz_label=seat.sitz_label,
                        sektor=seat.sektor,
                        besetzt=seat.besetzt,
                        vorstellung_id=seat.vorstellung_id,
                    )
                    for seat in sitzplaetze
                ],
            )
            film.vorstellungen.append(vorstellung)
        return film

    def list_all(self) -> list[Film]:
        with Session(engine) as session:
            rows = session.exec(select(FilmORM)).all()
            return [self._to_domain(session, row) for row in rows]

    def get_by_id(self, film_id: UUID) -> Film | None:
        with Session(engine) as session:
            row = session.get(FilmORM, film_id)
            return self._to_domain(session, row) if row else None

    def find(
        self,
        filter_data: dict[str, object] | None = None,
        sort: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> list[Film]:
        filter_data = filter_data or {}
        search_term = filter_data.get("search_term") if isinstance(filter_data.get("search_term"), str) else None
        sprache_id = filter_data.get("sprache_id") if isinstance(filter_data.get("sprache_id"), UUID) else None
        kategorie_id = filter_data.get("kategorie_id") if isinstance(filter_data.get("kategorie_id"), UUID) else None
        max_altersfreigabe = filter_data.get("max_altersfreigabe") if isinstance(filter_data.get("max_altersfreigabe"), int) else None

        films = self.list_all()
        films = [
            film
            for film in films
            if film.matches_filters(
                search_term=search_term,
                sprache_id=sprache_id,
                kategorie_id=kategorie_id,
                max_altersfreigabe=max_altersfreigabe,
            )
        ]
        if sort:
            reverse = sort.startswith("-")
            sort_field = sort[1:] if reverse else sort
            films.sort(key=lambda film: getattr(film, sort_field, None), reverse=reverse)

        start = max(page - 1, 0) * size
        return films[start:start + size]

    def _sync_film_relations(self, session: Session, film: Film) -> None:
        for link in session.exec(select(FilmSprache).where(FilmSprache.film_id == film.film_id)).all():
            session.delete(link)
        for link in session.exec(select(FilmKategorie).where(FilmKategorie.film_id == film.film_id)).all():
            session.delete(link)
        for vorstellung in session.exec(select(VorstellungORM).where(VorstellungORM.film_id == film.film_id)).all():
            for seat in session.exec(select(SitzplatzORM).where(SitzplatzORM.vorstellung_id == vorstellung.vorstellung_id)).all():
                session.delete(seat)
            session.delete(vorstellung)

        for sprache_id in film.sprache_ids:
            session.add(FilmSprache(film_id=film.film_id, sprache_id=sprache_id))
        for kategorie_id in film.kategorie_ids:
            session.add(FilmKategorie(film_id=film.film_id, kategorie_id=kategorie_id))

        for vorstellung in film.vorstellungen:
            vorstellung_row = VorstellungORM(
                vorstellung_id=vorstellung.vorstellung_id,
                film_id=film.film_id,
                saal=vorstellung.saal,
                ort=vorstellung.ort,
                startzeit=vorstellung.startzeit,
                endzeit=vorstellung.endzeit,
            )
            session.add(vorstellung_row)
            session.flush()
            for seat in vorstellung.sitzplaetze:
                session.add(
                    SitzplatzORM(
                        sitzplatz_id=seat.sitzplatz_id,
                        vorstellung_id=vorstellung_row.vorstellung_id,
                        sitz_label=seat.sitz_label,
                        sektor=seat.sektor,
                        besetzt=seat.besetzt,
                    )
                )

    def save(self, film: Film) -> Film:
        with Session(engine) as session:
            existing = session.get(FilmORM, film.film_id)
            if existing is None:
                existing = FilmORM(
                    film_id=film.film_id,
                    titel=film.titel,
                    beschreibung=film.beschreibung,
                    altersfreigabe=film.altersfreigabe,
                    coverbild_url=film.coverbild_url,
                    hauptdarsteller=film.hauptdarsteller,
                    erscheinungsdatum=film.erscheinungsdatum,
                    basispreis=film.basispreis,
                    aktiv=film.aktiv,
                )
                session.add(existing)
            else:
                existing.titel = film.titel
                existing.beschreibung = film.beschreibung
                existing.altersfreigabe = film.altersfreigabe
                existing.coverbild_url = film.coverbild_url
                existing.hauptdarsteller = film.hauptdarsteller
                existing.erscheinungsdatum = film.erscheinungsdatum
                existing.basispreis = film.basispreis
                existing.aktiv = film.aktiv

            session.flush()
            self._sync_film_relations(session, film)
            session.commit()
            session.refresh(existing)
            return self._to_domain(session, existing)

    def delete(self, film_id: UUID) -> None:
        with Session(engine) as session:
            row = session.get(FilmORM, film_id)
            if row is None:
                return
            for link in session.exec(select(FilmlisteKunde).where(FilmlisteKunde.film_id == film_id)).all():
                session.delete(link)
            for link in session.exec(select(FilmSprache).where(FilmSprache.film_id == film_id)).all():
                session.delete(link)
            for link in session.exec(select(FilmKategorie).where(FilmKategorie.film_id == film_id)).all():
                session.delete(link)
            for vorstellung in session.exec(select(VorstellungORM).where(VorstellungORM.film_id == film_id)).all():
                for seat in session.exec(select(SitzplatzORM).where(SitzplatzORM.vorstellung_id == vorstellung.vorstellung_id)).all():
                    session.delete(seat)
                session.delete(vorstellung)
            session.delete(row)
            session.commit()

    def get_vorstellung_by_id(self, vorstellung_id: UUID) -> Vorstellung | None:
        with Session(engine) as session:
            row = session.get(VorstellungORM, vorstellung_id)
            if row is None:
                return None
            sitzplaetze = session.exec(select(SitzplatzORM).where(SitzplatzORM.vorstellung_id == vorstellung_id)).all()
            return Vorstellung(
                vorstellung_id=row.vorstellung_id,
                film_id=row.film_id,
                saal=row.saal,
                ort=row.ort,
                startzeit=row.startzeit,
                endzeit=row.endzeit,
                sitzplaetze=[
                    Sitzplatz(
                        sitzplatz_id=seat.sitzplatz_id,
                        sitz_label=seat.sitz_label,
                        sektor=seat.sektor,
                        besetzt=seat.besetzt,
                        vorstellung_id=seat.vorstellung_id,
                    )
                    for seat in sitzplaetze
                ],
            )

    def list_vorstellungen_by_film(self, film_id: UUID) -> list[Vorstellung]:
        with Session(engine) as session:
            rows = session.exec(select(VorstellungORM).where(VorstellungORM.film_id == film_id)).all()
            return [self.get_vorstellung_by_id(row.vorstellung_id) for row in rows if row is not None]

    def list_available_seats(self, vorstellung_id: UUID) -> list[Sitzplatz]:
        with Session(engine) as session:
            rows = session.exec(
                select(SitzplatzORM).where(SitzplatzORM.vorstellung_id == vorstellung_id, SitzplatzORM.besetzt == False)
            ).all()
            return [
                Sitzplatz(
                    sitzplatz_id=row.sitzplatz_id,
                    sitz_label=row.sitz_label,
                    sektor=row.sektor,
                    besetzt=row.besetzt,
                    vorstellung_id=row.vorstellung_id,
                )
                for row in rows
            ]

    def reserve_seat(self, vorstellung_id: UUID, sitzplatz_id: UUID) -> bool:
        with Session(engine) as session:
            row = session.get(SitzplatzORM, sitzplatz_id)
            if row is None or row.vorstellung_id != vorstellung_id or row.besetzt:
                return False
            row.besetzt = True
            session.add(row)
            session.commit()
            return True

    def release_seat(self, vorstellung_id: UUID, sitzplatz_id: UUID) -> bool:
        with Session(engine) as session:
            row = session.get(SitzplatzORM, sitzplatz_id)
            if row is None or row.vorstellung_id != vorstellung_id:
                return False
            row.besetzt = False
            session.add(row)
            session.commit()
            return True

    def count_tickets_sold(self, film_id: UUID) -> int:
        with Session(engine) as session:
            showtimes = session.exec(select(VorstellungORM.vorstellung_id).where(VorstellungORM.film_id == film_id)).all()
            if not showtimes:
                return 0
            total = 0
            for vorstellung_id in showtimes:
                total += len(
                    session.exec(select(SitzplatzORM).where(SitzplatzORM.vorstellung_id == vorstellung_id, SitzplatzORM.besetzt == True)).all()
                )
            return total

