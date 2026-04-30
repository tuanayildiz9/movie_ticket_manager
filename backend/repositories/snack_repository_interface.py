from abc import ABC, abstractmethod
from uuid import UUID

from backend.models import Snack


class ISnackRepository(ABC):
    @abstractmethod
    def create(self, snack: Snack) -> Snack:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, snack_id: UUID) -> Snack | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Snack]:
        raise NotImplementedError
