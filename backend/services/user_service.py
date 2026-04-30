from datetime import date
from uuid import UUID

from backend.models import Kunde, Zahlungsart

from backend.repositories.user_repository_interface import IUserRepository


class UserService:
    def __init__(self, user_repo: IUserRepository) -> None:
        self.user_repo = user_repo

    def register(self, data: dict[str, object]) -> Kunde:
        zahlungsart_value = data.get("zahlungsart")
        zahlungsart = None
        if isinstance(zahlungsart_value, Zahlungsart):
            zahlungsart = zahlungsart_value
        elif isinstance(zahlungsart_value, str):
            zahlungsart = Zahlungsart(name=zahlungsart_value)

        geburtsdatum_value = data.get("geburtsdatum")
        geburtsdatum = geburtsdatum_value if isinstance(geburtsdatum_value, date) else date.today()

        kunde = Kunde(
            vorname=str(data.get("vorname", "")),
            nachname=str(data.get("nachname", "")),
            adresse=str(data.get("adresse", "")),
            plz=str(data.get("plz", "")),
            geburtsdatum=geburtsdatum,
            telefonnummer=str(data.get("telefonnummer", "")),
            email=str(data.get("email", "")).lower(),
            zahlungsart=zahlungsart,
        )
        passwort = str(data.get("passwort", ""))
        if passwort:
            kunde.set_password(passwort)
        return self.user_repo.create(kunde)

    def authenticate(self, email: str, password: str) -> Kunde | None:
        kunde = self.user_repo.get_by_email(email)
        if kunde and kunde.check_password(password):
            return kunde
        return None

    def get_profile(self, kunde_id: UUID) -> Kunde | None:
        return self.user_repo.get_by_id(kunde_id)

    def update_profile(self, kunde_id: UUID, data: dict[str, object]) -> Kunde:
        kunde = self.user_repo.get_by_id(kunde_id)
        if kunde is None:
            raise ValueError("Kunde wurde nicht gefunden.")
        kunde.update_profile(data)
        return self.user_repo.update(kunde)

    def save_movie(self, kunde_id: UUID, film_id: UUID) -> Kunde:
        kunde = self.user_repo.get_by_id(kunde_id)
        if kunde is None:
            raise ValueError("Kunde wurde nicht gefunden.")
        kunde.add_saved_film(film_id)
        return self.user_repo.update(kunde)

    def remove_saved_movie(self, kunde_id: UUID, film_id: UUID) -> Kunde:
        kunde = self.user_repo.get_by_id(kunde_id)
        if kunde is None:
            raise ValueError("Kunde wurde nicht gefunden.")
        kunde.remove_saved_film(film_id)
        return self.user_repo.update(kunde)

    def add_category_preference(self, kunde_id: UUID, kategorie_id: UUID) -> Kunde:
        kunde = self.user_repo.get_by_id(kunde_id)
        if kunde is None:
            raise ValueError("Kunde wurde nicht gefunden.")
        kunde.add_category_preference(kategorie_id)
        return self.user_repo.update(kunde)
