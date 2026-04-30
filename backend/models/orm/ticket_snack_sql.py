from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .ticket_sql import Ticket
    from .snack_sql import Snack


class TicketSnack(SQLModel, table=True):
    __tablename__ = "ticket_snack"

    ticket_id: UUID = Field(foreign_key="ticket.ticket_id", primary_key=True)
    snack_id: UUID = Field(foreign_key="snack.snack_id", primary_key=True)
    anzahl: int = Field(default=1)

    ticket: "Ticket" = Relationship(back_populates="snack_lines")
    snack: "Snack" = Relationship(back_populates="ticket_lines")
