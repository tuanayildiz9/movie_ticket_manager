from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel


class FilmlisteKunde(SQLModel, table=True):
    __tablename__ = "filmliste_kunde"

    kunde_id: UUID = Field(foreign_key="kunde.kunde_id", primary_key=True)
    film_id: UUID = Field(foreign_key="film.film_id", primary_key=True)
    gespeichert_am: datetime = Field(default_factory=datetime.utcnow)
