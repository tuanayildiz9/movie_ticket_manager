from uuid import UUID

from sqlmodel import Session, select

from backend.models import Account
from backend.models.orm.account_sql import Account as AccountORM
from config.database import engine


class AccountRepository:
    def _to_domain(self, row: AccountORM) -> Account:
        return Account(
            account_id=row.account_id,
            email=row.email,
            passwort_hash=row.passwort_hash,
            rolle=row.rolle,
            aktiv=row.aktiv,
        )

    def create(self, account: Account) -> Account:
        with Session(engine) as session:
            row = AccountORM(
                account_id=account.account_id,
                email=account.email.lower(),
                passwort_hash=account.passwort_hash,
                rolle=account.rolle,
                aktiv=account.aktiv,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return self._to_domain(row)

    def get_by_id(self, account_id: UUID) -> Account | None:
        with Session(engine) as session:
            row = session.get(AccountORM, account_id)
            return self._to_domain(row) if row else None

    def get_by_email(self, email: str) -> Account | None:
        with Session(engine) as session:
            row = session.exec(select(AccountORM).where(AccountORM.email == email.lower())).first()
            return self._to_domain(row) if row else None

    def update(self, account: Account) -> Account:
        with Session(engine) as session:
            row = session.get(AccountORM, account.account_id)
            if row is None:
                return self.create(account)

            row.email = account.email.lower()
            row.passwort_hash = account.passwort_hash
            row.rolle = account.rolle
            row.aktiv = account.aktiv
            session.add(row)
            session.commit()
            session.refresh(row)
            return self._to_domain(row)

    def delete(self, account_id: UUID) -> None:
        with Session(engine) as session:
            row = session.get(AccountORM, account_id)
            if row is None:
                return
            session.delete(row)
            session.commit()

    def list_all(self) -> list[Account]:
        with Session(engine) as session:
            rows = session.exec(select(AccountORM)).all()
            return [self._to_domain(row) for row in rows]