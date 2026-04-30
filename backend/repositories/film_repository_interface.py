from abc import ABC, abstractmethod
from uuid import UUID

from backend.models import Film, Sitzplatz, Vorstellung


class IFilmRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[Film]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, film_id: UUID) -> Film | None:
        raise NotImplementedError

    @abstractmethod
    def find(
        self,
        filter_data: dict[str, object] | None = None,
        sort: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> list[Film]:
        raise NotImplementedError

    @abstractmethod
    def save(self, film: Film) -> Film:
        raise NotImplementedError

    @abstractmethod
    def delete(self, film_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_vorstellung_by_id(self, vorstellung_id: UUID) -> Vorstellung | None:
        raise NotImplementedError

    @abstractmethod
    def list_vorstellungen_by_film(self, film_id: UUID) -> list[Vorstellung]:
        raise NotImplementedError

    @abstractmethod
    def list_available_seats(self, vorstellung_id: UUID) -> list[Sitzplatz]:
        raise NotImplementedError

    @abstractmethod
    def reserve_seat(self, vorstellung_id: UUID, sitzplatz_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    def release_seat(self, vorstellung_id: UUID, sitzplatz_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    def count_tickets_sold(self, film_id: UUID) -> int:
        raise NotImplementedError
