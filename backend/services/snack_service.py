from uuid import UUID

from backend.models import Snack
from backend.repositories.snack_repository import SnackRepository


class SnackService:
    def __init__(self, snack_repo: SnackRepository) -> None:
        self.snack_repo = snack_repo

    def list_all_snacks(self) -> list[Snack]:
        return self.snack_repo.list_all()

    def get_snack_by_id(self, snack_id: UUID) -> Snack | None:
        return self.snack_repo.get_by_id(snack_id)