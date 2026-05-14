from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .film_sql import Film
    from .sitzplatz_sql import Sitzplatz
    from .ticket_sql import Ticket


class Vorstellung(SQLModel, table=True):
    __tablename__ = "vorstellung"

    vorstellung_id: UUID = Field(default_factory=uuid4, primary_key=True)
    film_id: UUID = Field(foreign_key="film.film_id", index=True)
    saal: str = Field(default="", index=True)
    ort: str = Field(default="", index=True)
    startzeit: datetime = Field(default_factory=datetime.utcnow, index=True)
    endzeit: datetime | None = None

    film: "Film" = Relationship(back_populates="vorstellungen")
    sitzplaetze: list["Sitzplatz"] = Relationship(back_populates="vorstellung")
    tickets: list["Ticket"] = Relationship(back_populates="vorstellung")
