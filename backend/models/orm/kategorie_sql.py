from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from .film_kategorie_sql import FilmKategorie
from .kunden_kategorie_praeferenz_sql import KundenKategoriePraeferenz

if TYPE_CHECKING:
    from .film_sql import Film
    from .kunde_sql import Kunde


class Kategorie(SQLModel, table=True):
    __tablename__ = "kategorie"

    kategorie_id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(default="", index=True)

    filme: list["Film"] = Relationship(back_populates="kategorien", link_model=FilmKategorie)
    interessenten: list["Kunde"] = Relationship(
        back_populates="kategorien_praeferenzen",
        link_model=KundenKategoriePraeferenz,
    )
