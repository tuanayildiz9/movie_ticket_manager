from __future__ import annotations

from uuid import UUID

from sqlmodel import Field, SQLModel


class FilmSprache(SQLModel, table=True):
    __tablename__ = "film_sprache"

    film_id: UUID = Field(foreign_key="film.film_id", primary_key=True)
    sprache_id: UUID = Field(foreign_key="sprache.sprache_id", primary_key=True)
