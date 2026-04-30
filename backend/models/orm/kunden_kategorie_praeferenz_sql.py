from __future__ import annotations

from uuid import UUID

from sqlmodel import Field, SQLModel


class KundenKategoriePraeferenz(SQLModel, table=True):
    __tablename__ = "kunden_kategorie_praeferenz"

    kunde_id: UUID = Field(foreign_key="kunde.kunde_id", primary_key=True)
    kategorie_id: UUID = Field(foreign_key="kategorie.kategorie_id", primary_key=True)
