from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from .vorstellung import Vorstellung


@dataclass
class Film:
    film_id: UUID = field(default_factory=uuid4)
    titel: str = ""
    beschreibung: str = ""
    altersfreigabe: int = 0
    coverbild_url: str = ""
    hauptdarsteller: str = ""
    erscheinungsdatum: date = field(default_factory=date.today)
    basispreis: Decimal = Decimal("0.00")
    sprache_ids: list[UUID] = field(default_factory=list)
    kategorie_ids: list[UUID] = field(default_factory=list)
    vorstellungen: list[Vorstellung] = field(default_factory=list)
    aktiv: bool = True

    def get_summary(self) -> str:
        return f"{self.titel} ({self.erscheinungsdatum.isoformat()}) - {self.altersfreigabe}+"

    def is_available(self, reference_date: date | None = None) -> bool:
        reference_date = reference_date or date.today()
        return self.aktiv and self.erscheinungsdatum <= reference_date

    def matches_filters(
        self,
        search_term: str | None = None,
        sprache_id: UUID | list[UUID] | None = None,
        kategorie_id: UUID | list[UUID] | None = None,
        max_altersfreigabe: int | None = None,
    ) -> bool:
        if search_term:
            haystack = " ".join([self.titel, self.hauptdarsteller]).lower()
            if search_term.lower() not in haystack:
                return False
        if sprache_id:
            sprache_ids = [sprache_id] if isinstance(sprache_id, UUID) else sprache_id
            if not any(uid in self.sprache_ids for uid in sprache_ids):
                return False
        if kategorie_id:
            kategorie_ids = [kategorie_id] if isinstance(kategorie_id, UUID) else kategorie_id
            if not any(uid in self.kategorie_ids for uid in kategorie_ids):
                return False
        if max_altersfreigabe is not None and self.altersfreigabe > max_altersfreigabe:
            return False
        return True

    def add_language(self, sprache_id: UUID) -> None:
        if sprache_id not in self.sprache_ids:
            self.sprache_ids.append(sprache_id)

    def add_category(self, kategorie_id: UUID) -> None:
        if kategorie_id not in self.kategorie_ids:
            self.kategorie_ids.append(kategorie_id)

    def add_vorstellung(self, vorstellung: Vorstellung) -> None:
        self.vorstellungen.append(vorstellung)
