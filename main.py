from datetime import date

from backend.repositories import (
	AccountRepository,
	BestellungRepository,
	BewertungRepository,
	FilmRepository,
	KundeRepository,
	SnackRepository,
)
from backend.services import AdminService, BestellungService, FilmService, UserService
from backend.seed import seed_database
from config.database import create_db_and_tables


def build_application() -> tuple[UserService, FilmService, BestellungService, AdminService]:
	# ensure DB and tables exist
	create_db_and_tables()

	account_repo = AccountRepository()
	kunde_repo = KundeRepository()
	film_repo = FilmRepository()
	bestellung_repo = BestellungRepository()
	bewertung_repo = BewertungRepository()
	snack_repo = SnackRepository()

	film_service = FilmService(film_repo=film_repo, bewertung_repo=bewertung_repo, kunde_repo=kunde_repo)
	user_service = UserService(account_repo=account_repo, kunde_repo=kunde_repo)
	bestellung_service = BestellungService(
		bestellung_repo=bestellung_repo,
		film_repo=film_repo,
		kunde_repo=kunde_repo,
		snack_repo=snack_repo,
	)
	admin_service = AdminService(film_repo=film_repo, bestellung_repo=bestellung_repo)
	return user_service, film_service, bestellung_service, admin_service


def _read_text(prompt: str) -> str:
	return input(prompt).strip()


def _read_required_text(prompt: str) -> str:
	value = _read_text(prompt)
	if not value:
		raise ValueError("Eingabe darf nicht leer sein.")
	return value


def _read_date(prompt: str) -> date:
	value = _read_required_text(prompt)
	try:
		return date.fromisoformat(value)
	except ValueError as exc:
		raise ValueError("Bitte ein Datum im Format JJJJ-MM-TT eingeben.") from exc


def register_customer_account(user_service: UserService) -> None:
	print("\nKundenkonto anlegen")
	data = {
		"vorname": _read_required_text("Vorname: "),
		"nachname": _read_required_text("Nachname: "),
		"email": _read_required_text("E-Mail: "),
		"passwort": _read_required_text("Passwort: "),
		"geburtsdatum": _read_date("Geburtsdatum (JJJJ-MM-TT): "),
		"adresse": _read_text("Adresse (optional): "),
		"plz": _read_text("PLZ (optional): "),
		"telefonnummer": _read_text("Telefonnummer (optional): "),
		"zahlungsart": _read_text("Zahlungsart (optional): "),
	}
	kunde = user_service.register(data)
	print(f"Konto erfolgreich angelegt fuer {kunde.full_name()}.")
	print(f"Kunden-ID: {kunde.kunde_id}")
	print(f"Account-ID: {kunde.account_id}")


def main() -> None:
	seed_database()
	user_service, film_service, bestellung_service, admin_service = build_application()

	print("Movie Ticket Manager ist gestartet.")
	print(f"Verfuegbare Services: {user_service.__class__.__name__}, {film_service.__class__.__name__}, {bestellung_service.__class__.__name__}, {admin_service.__class__.__name__}")

	if __import__("sys").stdin.isatty():
		antwort = _read_text("Moechtest du ein Kundenkonto anlegen? (j/n): ").lower()
		if antwort.startswith("j"):
			try:
				register_customer_account(user_service)
			except ValueError as exc:
				print(f"Registrierung fehlgeschlagen: {exc}")


if __name__ == "__main__":
	main()

