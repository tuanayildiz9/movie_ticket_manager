from abc import ABC, abstractmethod
from uuid import UUID

from backend.models import Kunde


class IUserRepository(ABC):
    @abstractmethod
    def create(self, kunde: Kunde) -> Kunde:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, kunde_id: UUID) -> Kunde | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, email: str) -> Kunde | None:
        raise NotImplementedError

    @abstractmethod
    def update(self, kunde: Kunde) -> Kunde:
        raise NotImplementedError

    @abstractmethod
    def delete(self, kunde_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Kunde]:
        raise NotImplementedError
