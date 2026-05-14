from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, Numeric
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .bestellung_sql import Bestellung
    from .film_sql import Film
    from .sitzplatz_sql import Sitzplatz
    from .ticket_snack_sql import TicketSnack
    from .vorstellung_sql import Vorstellung


class Ticket(SQLModel, table=True):
    __tablename__ = "ticket"

    ticket_id: UUID = Field(default_factory=uuid4, primary_key=True)
    bestellung_id: UUID = Field(foreign_key="bestellung.bestellung_id", index=True)
    film_id: UUID = Field(foreign_key="film.film_id", index=True)
    vorstellung_id: UUID = Field(foreign_key="vorstellung.vorstellung_id", index=True)
    sitzplatz_id: UUID = Field(foreign_key="sitzplatz.sitzplatz_id", index=True)
    verguenstigungsart: str = Field(default="regulaer", index=True)
    preis: Decimal = Field(default=Decimal("0.00"), sa_column=Column(Numeric(10, 2), nullable=False))

    bestellung: "Bestellung" = Relationship(back_populates="tickets")
    film: "Film" = Relationship(back_populates="tickets")
    vorstellung: "Vorstellung" = Relationship(back_populates="tickets")
    sitzplatz: "Sitzplatz" = Relationship(back_populates="ticket")
    snack_lines: list["TicketSnack"] = Relationship(back_populates="ticket")
