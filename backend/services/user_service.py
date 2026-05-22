from datetime import date
from uuid import UUID

from backend.models import Account, Kunde, Zahlungsart

from backend.repositories.account_repository import AccountRepository
from backend.repositories.kunde_repository import KundeRepository


class UserService:
    def __init__(self, account_repo: AccountRepository, kunde_repo: KundeRepository) -> None:
        self.account_repo = account_repo
        self.kunde_repo = kunde_repo

    def _require_text(self, value: object, field_name: str) -> str:
        text = str(value).strip()
        if not text:
            raise ValueError(f"{field_name} darf nicht leer sein.")
        return text

    def register(self, data: dict[str, object]) -> Kunde:
        email = self._require_text(data.get("email", ""), "E-Mail").lower()
        if self.account_repo.get_by_email(email) is not None:
            raise ValueError("E-Mail wird bereits verwendet.")

        account = Account(email=email, rolle="kunde")
        passwort = self._require_text(data.get("passwort", ""), "Passwort")
        account.set_password(passwort)
        account = self.account_repo.create(account)

        zahlungsart_value = data.get("zahlungsart")
        zahlungsart = None
        if isinstance(zahlungsart_value, Zahlungsart):
            zahlungsart = zahlungsart_value
        elif isinstance(zahlungsart_value, str):
            zahlungsart = Zahlungsart(name=zahlungsart_value)

        geburtsdatum_value = data.get("geburtsdatum")
        geburtsdatum = geburtsdatum_value if isinstance(geburtsdatum_value, date) else date.today()

        kunde = Kunde(
            account_id=account.account_id,
            vorname=self._require_text(data.get("vorname", ""), "Vorname"),
            nachname=self._require_text(data.get("nachname", ""), "Nachname"),
            adresse=str(data.get("adresse", "")),
            plz=str(data.get("plz", "")),
            ort=str(data.get("ort", "")),
            geburtsdatum=geburtsdatum,
            telefonnummer=str(data.get("telefonnummer", "")),
            zahlungsart=zahlungsart,
        )
        return self.kunde_repo.create(kunde)

    def authenticate(self, email: str, password: str) -> Account | None:
        account = self.account_repo.get_by_email(email)
        if account and account.check_password(password):
            return account
        return None

    def get_profile(self, kunde_id: UUID) -> Kunde | None:
        return self.kunde_repo.get_by_id(kunde_id)

    def get_profile_by_account_id(self, account_id: UUID) -> Kunde | None:
        return self.kunde_repo.get_by_account_id(account_id)

    def update_profile(self, kunde_id: UUID, data: dict[str, object]) -> Kunde:
        kunde = self.kunde_repo.get_by_id(kunde_id)
        if kunde is None:
            raise ValueError("Kunde wurde nicht gefunden.")
        kunde.update_profile(data)
        return self.kunde_repo.update(kunde)

    def save_movie(self, kunde_id: UUID, film_id: UUID) -> Kunde:
        kunde = self.kunde_repo.get_by_id(kunde_id)
        if kunde is None:
            raise ValueError("Kunde wurde nicht gefunden.")
        kunde.add_saved_film(film_id)
        return self.kunde_repo.update(kunde)

    def remove_saved_movie(self, kunde_id: UUID, film_id: UUID) -> Kunde:
        kunde = self.kunde_repo.get_by_id(kunde_id)
        if kunde is None:
            raise ValueError("Kunde wurde nicht gefunden.")
        kunde.remove_saved_film(film_id)
        return self.kunde_repo.update(kunde)

    def add_category_preference(self, kunde_id: UUID, kategorie_id: UUID) -> Kunde:
        kunde = self.kunde_repo.get_by_id(kunde_id)
        if kunde is None:
            raise ValueError("Kunde wurde nicht gefunden.")
        kunde.add_category_preference(kategorie_id)
        return self.kunde_repo.update(kunde)
