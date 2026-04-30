from abc import ABC, abstractmethod
from uuid import UUID

from backend.models import Bewertung


class IBewertungRepository(ABC):
    @abstractmethod
    def create(self, bewertung: Bewertung) -> Bewertung:
        raise NotImplementedError

    @abstractmethod
    def list_by_film(self, film_id: UUID) -> list[Bewertung]:
        raise NotImplementedError

    @abstractmethod
    def list_by_kunde(self, kunde_id: UUID) -> list[Bewertung]:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Bewertung]:
        raise NotImplementedError
