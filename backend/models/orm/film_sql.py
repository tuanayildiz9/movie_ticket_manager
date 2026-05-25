from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, Numeric
from sqlmodel import Field, Relationship, SQLModel

from .film_kategorie_sql import FilmKategorie
from .film_sprache_sql import FilmSprache

if TYPE_CHECKING:
    from .bewertung_sql import Bewertung
    from .kategorie_sql import Kategorie
    from .sprache_sql import Sprache
    from .ticket_sql import Ticket
    from .vorstellung_sql import Vorstellung


class Film(SQLModel, table=True):
    __tablename__ = "film"

    film_id: UUID = Field(default_factory=uuid4, primary_key=True)
    titel: str = Field(default="", index=True)
    beschreibung: str = Field(default="")
    altersfreigabe: int = Field(default=0, index=True)
    coverbild_url: str = Field(default="")
    hauptdarsteller: str = Field(default="")
    erscheinungsdatum: date = Field(default_factory=date.today, index=True)
    basispreis: Decimal = Field(default=Decimal("0.00"), sa_column=Column(Numeric(10, 2), nullable=False))
    aktiv: bool = Field(default=True)

    sprachen: list["Sprache"] = Relationship(back_populates="filme", link_model=FilmSprache)
    kategorien: list["Kategorie"] = Relationship(back_populates="filme", link_model=FilmKategorie)
    vorstellungen: list["Vorstellung"] = Relationship(back_populates="film")
    bewertungen: list["Bewertung"] = Relationship(back_populates="film")
    tickets: list["Ticket"] = Relationship(back_populates="film")
