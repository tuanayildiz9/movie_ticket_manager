from decimal import Decimal
from uuid import UUID

from backend.models import Bewertung, Film

from backend.repositories.bewertung_repository_interface import IBewertungRepository
from backend.repositories.film_repository_interface import IFilmRepository


class FilmService:
    def __init__(self, film_repo: IFilmRepository, bewertung_repo: IBewertungRepository) -> None:
        self.film_repo = film_repo
        self.bewertung_repo = bewertung_repo

    def list_current_films(
        self,
        filter_data: dict[str, object] | None = None,
        sort: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> list[Film]:
        return self.film_repo.find(filter_data=filter_data, sort=sort, page=page, size=size)

    def get_film_details(self, film_id: UUID) -> Film | None:
        return self.film_repo.get_by_id(film_id)

    def rate_film(self, kunde_id: UUID, film_id: UUID, score: int, comment: str) -> Bewertung:
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
