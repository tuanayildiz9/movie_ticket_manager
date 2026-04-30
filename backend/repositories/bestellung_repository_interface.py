from abc import ABC, abstractmethod
from uuid import UUID

from backend.models import Bestellung


class IBestellungRepository(ABC):
    @abstractmethod
    def create(self, bestellung: Bestellung) -> Bestellung:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, bestellung_id: UUID) -> Bestellung | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_kunde(self, kunde_id: UUID) -> list[Bestellung]:
        raise NotImplementedError

    @abstractmethod
    def list_by_film(self, film_id: UUID) -> list[Bestellung]:
        raise NotImplementedError

    @abstractmethod
    def list_by_vorstellung(self, vorstellung_id: UUID) -> list[Bestellung]:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Bestellung]:
        raise NotImplementedError
