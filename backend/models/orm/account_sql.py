from hashlib import sha256
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Account(SQLModel, table=True):
    __tablename__ = "account"

    account_id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(default="", index=True, nullable=False, unique=True)
    passwort_hash: str = Field(default="")
    rolle: str = Field(default="kunde", index=True)
    aktiv: bool = Field(default=True, index=True)

    def set_password(self, plain_password: str) -> None:
        self.passwort_hash = sha256(plain_password.encode("utf-8")).hexdigest()