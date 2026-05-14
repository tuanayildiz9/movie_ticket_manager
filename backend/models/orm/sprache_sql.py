from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from .film_sprache_sql import FilmSprache

if TYPE_CHECKING:
    from .film_sql import Film


class Sprache(SQLModel, table=True):
    __tablename__ = "sprache"

    sprache_id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(default="", index=True)

    filme: list["Film"] = Relationship(back_populates="sprachen", link_model=FilmSprache)
