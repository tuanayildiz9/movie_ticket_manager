from dataclasses import dataclass, field
from datetime import date
from hashlib import sha256
from uuid import UUID, uuid4

from .zahlungsart import Zahlungsart


@dataclass
class Kunde:
    kunde_id: UUID = field(default_factory=uuid4)
    vorname: str = ""
    nachname: str = ""
    adresse: str = ""
    plz: str = ""
    geburtsdatum: date = field(default_factory=date.today)
    telefonnummer: str = ""
    email: str = ""
    passwort_hash: str = ""
    zahlungsart: Zahlungsart | None = None
    gespeicherte_filme: list[UUID] = field(default_factory=list)
    kategorien_praeferenzen: list[UUID] = field(default_factory=list)

    def full_name(self) -> str:
        return f"{self.vorname} {self.nachname}".strip()

    def age(self, reference_date: date | None = None) -> int:
        reference_date = reference_date or date.today()
        years = reference_date.year - self.geburtsdatum.year
        before_birthday = (reference_date.month, reference_date.day) < (
            self.geburtsdatum.month,
            self.geburtsdatum.day,
        )
        return years - int(before_birthday)

    def set_password(self, plain_password: str) -> None:
        self.passwort_hash = sha256(plain_password.encode("utf-8")).hexdigest()

    def check_password(self, plain_password: str) -> bool:
        return self.passwort_hash == sha256(plain_password.encode("utf-8")).hexdigest()

    def can_purchase(self, min_age: int = 0) -> bool:
        return self.age() >= min_age

    def add_saved_film(self, film_id: UUID) -> None:
        if film_id not in self.gespeicherte_filme:
            self.gespeicherte_filme.append(film_id)

    def remove_saved_film(self, film_id: UUID) -> None:
        if film_id in self.gespeicherte_filme:
            self.gespeicherte_filme.remove(film_id)

    def add_category_preference(self, kategorie_id: UUID) -> None:
        if kategorie_id not in self.kategorien_praeferenzen:
            self.kategorien_praeferenzen.append(kategorie_id)

    def update_profile(self, data: dict[str, object]) -> None:
        for key, value in data.items():
            if key == "passwort":
                self.set_password(str(value))
                continue
            if key == "zahlungsart":
                if isinstance(value, Zahlungsart):
                    self.zahlungsart = value
                elif isinstance(value, str):
                    self.zahlungsart = Zahlungsart(name=value)
                continue
            if hasattr(self, key):
                setattr(self, key, value)
