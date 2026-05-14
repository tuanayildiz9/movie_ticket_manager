from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .film_sql import Film
    from .kunde_sql import Kunde


class Bewertung(SQLModel, table=True):
    __tablename__ = "bewertung"

    bewertung_id: UUID = Field(default_factory=uuid4, primary_key=True)
    kunde_id: UUID = Field(foreign_key="kunde.kunde_id", index=True)
    film_id: UUID = Field(foreign_key="film.film_id", index=True)
    bewertung: int = Field(default=0, index=True)
    kommentar: str = Field(default="")
    bewertungsdatum: datetime = Field(default_factory=datetime.utcnow, index=True)

    kunde: "Kunde" = Relationship(back_populates="bewertungen")
    film: "Film" = Relationship(back_populates="bewertungen")
