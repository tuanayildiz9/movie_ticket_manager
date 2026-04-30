from decimal import Decimal
from uuid import UUID

from sqlmodel import Session, select

from backend.models import Snack
from backend.models.orm.snack_sql import Snack as SnackORM
from config.database import engine

from .snack_repository_interface import ISnackRepository


class SnackRepository(ISnackRepository):
    def _to_domain(self, row: SnackORM) -> Snack:
        return Snack(snack_id=row.snack_id, name=row.name, preis=row.preis)

    def create(self, snack: Snack) -> Snack:
        with Session(engine) as session:
            row = SnackORM(snack_id=snack.snack_id, name=snack.name, preis=snack.preis)
            session.add(row)
            session.commit()
            session.refresh(row)
            return self._to_domain(row)

    def get_by_id(self, snack_id: UUID) -> Snack | None:
        with Session(engine) as session:
            row = session.get(SnackORM, snack_id)
            return self._to_domain(row) if row else None

    def list_all(self) -> list[Snack]:
        with Session(engine) as session:
            rows = session.exec(select(SnackORM)).all()
            return [self._to_domain(row) for row in rows]
