from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, Numeric
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .kunde_sql import Kunde
    from .ticket_sql import Ticket


class Bestellung(SQLModel, table=True):
    __tablename__ = "bestellung"

    bestellung_id: UUID = Field(default_factory=uuid4, primary_key=True)
    kunde_id: UUID = Field(foreign_key="kunde.kunde_id", index=True)
    bestellungsdatum: datetime = Field(default_factory=datetime.utcnow, index=True)
    anzahl_tickets: int = Field(default=0)
    total_betrag: Decimal = Field(default=Decimal("0.00"), sa_column=Column(Numeric(10, 2), nullable=False))

    kunde: "Kunde" = Relationship(back_populates="bestellungen")
    tickets: list["Ticket"] = Relationship(back_populates="bestellung")
