from __future__ import annotations

from uuid import UUID

from sqlmodel import Field, SQLModel


class FilmKategorie(SQLModel, table=True):
    __tablename__ = "film_kategorie"

    film_id: UUID = Field(foreign_key="film.film_id", primary_key=True)
    kategorie_id: UUID = Field(foreign_key="kategorie.kategorie_id", primary_key=True)
