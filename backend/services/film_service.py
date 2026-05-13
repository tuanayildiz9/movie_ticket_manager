from decimal import Decimal
from uuid import UUID

from backend.models import Bewertung, Film

from backend.repositories.bewertung_repository import BewertungRepository
from backend.repositories.film_repository import FilmRepository
from backend.repositories.kunde_repository import KundeRepository
from sqlmodel import Session, select
from backend.models.orm.kategorie_sql import Kategorie as KategorieORM
from backend.models.orm.sprache_sql import Sprache as SpracheORM
from config.database import engine


class FilmService:
    def __init__(
        self,
        film_repo: FilmRepository,
        bewertung_repo: BewertungRepository,
        kunde_repo: KundeRepository | None = None,
    ) -> None:
        self.film_repo = film_repo
        self.bewertung_repo = bewertung_repo
        self.kunde_repo = kunde_repo

    def list_current_films(
        self,
        filter_data: dict[str, object] | None = None,
        sort: str | None = None,
        page: int = 1,
        size: int = 10,
        summaries: bool = False,
    ) -> list[Film] | list[dict[str, object]]:
        films = self.film_repo.list_current(filter_data=filter_data, sort=sort, page=page, size=size)
        if summaries:
            return [
                {
                    "film_id": film.film_id,
                    "titel": film.titel,
                    "coverbild_url": film.coverbild_url,
                    "basispreis": film.basispreis,
                    "altersfreigabe": film.altersfreigabe,
                }
                for film in films
            ]
        return films

    def get_film_details(self, film_id: UUID) -> Film | None:
        return self.film_repo.get_by_id(film_id)

    def rate_film(self, kunde_id: UUID, film_id: UUID, score: int, comment: str) -> Bewertung:
        if self.kunde_repo is not None and self.kunde_repo.get_by_id(kunde_id) is None:
            raise ValueError("Kunde wurde nicht gefunden.")
        if self.film_repo.get_by_id(film_id) is None:
            raise ValueError("Film wurde nicht gefunden.")
        bewertung = Bewertung(kunde_id=kunde_id, film_id=film_id, bewertung=score, kommentar=comment)
        return self.bewertung_repo.create(bewertung)

    def get_average_rating(self, film_id: UUID) -> Decimal:
        ratings = self.bewertung_repo.list_by_film(film_id)
        if not ratings:
            return Decimal("0.00")
        average = sum(bewertung.bewertung for bewertung in ratings) / len(ratings)
        return Decimal(str(round(average, 2)))

    def filter_films(
        self,
        search_term: str | None = None,
        sprache_id: UUID | None = None,
        kategorie_id: UUID | None = None,
        max_altersfreigabe: int | None = None,
    ) -> list[Film]:
        return self.film_repo.find(
            filter_data={
                "search_term": search_term,
                "sprache_id": sprache_id,
                "kategorie_id": kategorie_id,
                "max_altersfreigabe": max_altersfreigabe,
            },
            sort=None,
            page=1,
            size=100,
        )

    def search_films(
        self,
        search_term: str | None = None,
        kategorie_name: str | None = None,
        sprache_name: str | None = None,
        max_altersfreigabe: int | None = None,
        sort: str | None = None,
        page: int = 1,
        size: int = 100,
    ) -> list[Film]:
        """Search and filter films by optional human-friendly names.

        Resolves `kategorie_name` and `sprache_name` to their UUIDs and delegates to the repository.
        """
        kategorie_id = None
        sprache_id = None
        with Session(engine) as session:
            if kategorie_name:
                k = session.exec(select(KategorieORM).where(KategorieORM.name == kategorie_name)).first()
                if k is not None:
                    kategorie_id = k.kategorie_id
            if sprache_name:
                s = session.exec(select(SpracheORM).where(SpracheORM.name == sprache_name)).first()
                if s is not None:
                    sprache_id = s.sprache_id

        return self.film_repo.find(
            filter_data={
                "search_term": search_term,
                "sprache_id": sprache_id,
                "kategorie_id": kategorie_id,
                "max_altersfreigabe": max_altersfreigabe,
            },
            sort=sort,
            page=page,
            size=size,
        )
