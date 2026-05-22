from datetime import date
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from .bestellung_sql import Bestellung
from .bewertung_sql import Bewertung
from .film_sql import Film
from .filmliste_kunde_sql import FilmlisteKunde
from .kategorie_sql import Kategorie
from .kunden_kategorie_praeferenz_sql import KundenKategoriePraeferenz
from .zahlungsart_sql import Zahlungsart


class Kunde(SQLModel, table=True):
    __tablename__ = "kunde"

    kunde_id: UUID = Field(default_factory=uuid4, primary_key=True)
    account_id: UUID | None = Field(default=None, foreign_key="account.account_id", index=True)
    vorname: str = Field(default="")
    nachname: str = Field(default="")
    adresse: str = Field(default="")
    plz: str = Field(default="")
    ort: str = Field(default="")
    geburtsdatum: date = Field(default_factory=date.today)
    telefonnummer: str = Field(default="")
    zahlungsart_id: UUID | None = Field(default=None, foreign_key="zahlungsart.zahlungsart_id")

    zahlungsart: Zahlungsart = Relationship(back_populates="kunden")
    gespeicherte_filme: list[Film] = Relationship(back_populates="gespeichert_von", link_model=FilmlisteKunde)
    kategorien_praeferenzen: list[Kategorie] = Relationship(
        back_populates="interessenten",
        link_model=KundenKategoriePraeferenz,
    )
    bestellungen: list[Bestellung] = Relationship(back_populates="kunde")
    bewertungen: list[Bewertung] = Relationship(back_populates="kunde")
