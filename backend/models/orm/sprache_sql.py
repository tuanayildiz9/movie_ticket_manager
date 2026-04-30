from __future__ import annotations

from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from .film_sprache_sql import FilmSprache


class Sprache(SQLModel, table=True):
    __tablename__ = "sprache"

    sprache_id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(default="", index=True)

    filme: list["Film"] = Relationship(back_populates="sprachen", link_model=FilmSprache)
