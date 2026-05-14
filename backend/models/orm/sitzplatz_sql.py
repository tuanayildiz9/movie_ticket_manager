from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .ticket_sql import Ticket
    from .vorstellung_sql import Vorstellung


class Sitzplatz(SQLModel, table=True):
    __tablename__ = "sitzplatz"

    sitzplatz_id: UUID = Field(default_factory=uuid4, primary_key=True)
    vorstellung_id: UUID = Field(foreign_key="vorstellung.vorstellung_id", index=True)
    sitz_label: str = Field(default="", index=True)
    sektor: str = Field(default="", index=True)
    besetzt: bool = Field(default=False)

    vorstellung: Optional["Vorstellung"] = Relationship(back_populates="sitzplaetze")
    ticket: Optional["Ticket"] = Relationship(back_populates="sitzplatz")
