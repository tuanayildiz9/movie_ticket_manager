from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .kunde_sql import Kunde


class Zahlungsart(SQLModel, table=True):
    __tablename__ = "zahlungsart"

    zahlungsart_id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(default="", index=True)

    kunden: list["Kunde"] = Relationship(back_populates="zahlungsart")
