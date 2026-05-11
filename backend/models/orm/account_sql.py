from __future__ import annotations

from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class Account(SQLModel, table=True):
    __tablename__ = "account"

    account_id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(default="", index=True, nullable=False, unique=True)
    passwort_hash: str = Field(default="")
    rolle: str = Field(default="kunde", index=True)
    aktiv: bool = Field(default=True, index=True)

    kunde: "Kunde | None" = Relationship(back_populates="account")