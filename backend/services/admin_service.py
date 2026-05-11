from uuid import UUID

from backend.repositories.bestellung_repository import BestellungRepository
from backend.repositories.film_repository import FilmRepository


class AdminService:
    def __init__(self, film_repo: FilmRepository, bestellung_repo: BestellungRepository) -> None:
        self.film_repo = film_repo
        self.bestellung_repo = bestellung_repo

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
