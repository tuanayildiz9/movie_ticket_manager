from __future__ import annotations

from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class Sitzplatz(SQLModel, table=True):
    __tablename__ = "sitzplatz"

    sitzplatz_id: UUID = Field(default_factory=uuid4, primary_key=True)
    vorstellung_id: UUID = Field(foreign_key="vorstellung.vorstellung_id", index=True)
    sitz_label: str = Field(default="", index=True)
    sektor: str = Field(default="", index=True)
    besetzt: bool = Field(default=False)

    vorstellung: "Vorstellung" = Relationship(back_populates="sitzplaetze")
    ticket: "Ticket | None" = Relationship(back_populates="sitzplatz")
