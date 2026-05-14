from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, Numeric
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .ticket_snack_sql import TicketSnack


class Snack(SQLModel, table=True):
    __tablename__ = "snack"

    snack_id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(default="", index=True)
    preis: Decimal = Field(default=Decimal("0.00"), sa_column=Column(Numeric(10, 2), nullable=False))

    ticket_lines: list["TicketSnack"] = Relationship(back_populates="snack")
