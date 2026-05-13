from datetime import date, datetime

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


def _read_int(prompt: str, min_value: int = 1) -> int:
	value = _read_required_text(prompt)
	try:
		parsed = int(value)
	except ValueError as exc:
		raise ValueError("Bitte eine gueltige Zahl eingeben.") from exc
	if parsed < min_value:
		raise ValueError(f"Die Zahl muss mindestens {min_value} sein.")
	return parsed


def _read_choice_index(prompt: str, count: int) -> int:
	choice = _read_int(prompt, min_value=1)
	if choice > count:
		raise ValueError("Auswahl ist ausserhalb des gueltigen Bereichs.")
	return choice - 1


def _read_discount_type() -> str:
	print("Verguenstigung: 1) regulaer  2) student  3) senior  4) kind")
	choice = _read_choice_index("Verguenstigung waehlen (1-4): ", 4)
	return ["regulaer", "student", "senior", "kind"][choice]


def _read_yes_no(prompt: str) -> bool:
	return _read_required_text(prompt).lower().startswith("j")


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


def login_customer_account(user_service: UserService):
	print("\nAnmelden")
	email = _read_required_text("E-Mail: ")
	passwort = _read_required_text("Passwort: ")
	account = user_service.authenticate(email=email, password=passwort)
	if account is None:
		raise ValueError("Anmeldung fehlgeschlagen.")
	kunde = user_service.get_profile_by_account_id(account.account_id)
	if kunde is None:
		raise ValueError("Zum Account wurde kein Kundenprofil gefunden.")
	print(f"Angemeldet als {kunde.full_name()}.")
	return account, kunde


def buy_tickets(bestellung_service: BestellungService, film_service: FilmService, kunde) -> None:

	films = film_service.list_current_films()
	if not films:
		raise ValueError("Es sind keine aktuellen Filme verfuegbar.")

	print("\nFilm auswaehlen")
	for index, film in enumerate(films, start=1):
		print(f"{index}) {film.titel} (Preis: {film.basispreis} CHF)")
	film_index = _read_choice_index("Film waehlen: ", len(films))
	film = films[film_index]
	if not film.vorstellungen:
		raise ValueError("Fuer diesen Film gibt es keine Vorstellungen.")

	print("\nVorstellung auswaehlen")
	for index, vorstellung in enumerate(film.vorstellungen, start=1):
		print(f"{index}) {vorstellung.startzeit} | {vorstellung.ort} | {vorstellung.saal}")
	vorstellung_index = _read_choice_index("Vorstellung waehlen: ", len(film.vorstellungen))
	vorstellung = film.vorstellungen[vorstellung_index]

	anzahl_tickets = _read_int("Anzahl Tickets: ", min_value=1)
	tickets: list[dict[str, object]] = []
	snacks: list[dict[str, object]] = []
	ticket_overview: list[dict[str, object]] = []
	snack_options = bestellung_service.snack_repo.list_all()

	for ticket_number in range(1, anzahl_tickets + 1):
		seats = bestellung_service.available_seats(vorstellung.vorstellung_id)
		if not seats:
			raise ValueError("Nicht genug freie Sitzplaetze fuer die gewuenschte Anzahl Tickets.")

		print(f"\nSitzplatz fuer Ticket {ticket_number} auswaehlen")
		for index, seat in enumerate(seats, start=1):
			print(f"{index}) {seat['sitz_label']} (Sektor {seat['sektor']})")
		seat_index = _read_choice_index("Sitzplatz waehlen: ", len(seats))
		selected_seat = seats[seat_index]

		tickets.append(
			{
				"film_id": film.film_id,
				"vorstellung_id": vorstellung.vorstellung_id,
				"sitzplatz_id": selected_seat["sitzplatz_id"],
				"verguenstigungsart": _read_discount_type(),
			}
		)
		ticket_overview.append(
			{
				"sitz_label": selected_seat["sitz_label"],
				"sitzplatz_id": selected_seat["sitzplatz_id"],
			}
		)

		if snack_options and _read_yes_no("Snacks zu diesem Ticket hinzufuegen? (j/n): "):
			while True:
				print("Snack-Auswahl")
				for index, snack in enumerate(snack_options, start=1):
					print(f"{index}) {snack.name} ({snack.preis} CHF)")
				snack_index = _read_choice_index("Snack waehlen: ", len(snack_options))
				snack_quantity = _read_int("Anzahl Snacks: ", min_value=1)
				snacks.append(
					{
						"ticket_index": len(tickets) - 1,
						"snack_id": snack_options[snack_index].snack_id,
						"anzahl": snack_quantity,
					}
				)
				if not _read_yes_no("Weiteren Snack zu diesem Ticket hinzufuegen? (j/n): "):
					break

	bestellung = bestellung_service.create_order(kunde_id=kunde.kunde_id, tickets=tickets, snacks=snacks)
	summary = bestellung_service.get_order_summary(
		bestellung.bestellung_id,
		film.titel,
		vorstellung.saal,
		vorstellung.ort,
		vorstellung.startzeit,
	)
	print("\nTicketkauf erfolgreich.")
	print(f"Bestell-ID: {summary['bestellung_id']}")
	print(f"Kunde: {kunde.full_name()}")
	print(f"Film: {summary['film_titel']}")
	print(f"Vorstellung: {summary['uhrzeit']} | {summary['ort']} | {summary['saal']}")
	print(f"Anzahl Tickets: {summary['anzahl_tickets']}")
	print(f"Total: {summary['total_betrag']} CHF")
	for index, ticket in enumerate(bestellung.tickets):
		ticket_meta = ticket_overview[index]
		print(f"- Sitzplatz {ticket_meta['sitz_label']}: {ticket.verguenstigungsart.value} | Preis {ticket.preis} CHF")
		for snack_line in ticket.snacks:
			snack = next((item for item in snack_options if item.snack_id == snack_line.snack_id), None)
			if snack is not None:
				print(f"  Snack: {snack.name} x{snack_line.anzahl}")


def main() -> None:
	seed_database()
	user_service, film_service, bestellung_service, admin_service = build_application()

	print("Movie Ticket Manager ist gestartet.")
	print(f"Verfuegbare Services: {user_service.__class__.__name__}, {film_service.__class__.__name__}, {bestellung_service.__class__.__name__}, {admin_service.__class__.__name__}")

	if __import__("sys").stdin.isatty():
		current_customer = None
		aktion = _read_text("Hast du bereits ein Kundenkonto? (j = anmelden / n = registrieren): ").lower()
		try:
			if aktion.startswith("j"):
				_, current_customer = login_customer_account(user_service)
			else:
				register_customer_account(user_service)
				current_customer = login_customer_account(user_service)[1]
		except ValueError as exc:
			print(f"Anmeldung/Registrierung fehlgeschlagen: {exc}")
			return

		antwort = _read_text("Moechtest du Tickets kaufen? (j/n): ").lower()
		if antwort.startswith("j"):
			try:
				buy_tickets(bestellung_service=bestellung_service, film_service=film_service, kunde=current_customer)
			except ValueError as exc:
				print(f"Ticketkauf fehlgeschlagen: {exc}")


if __name__ == "__main__":
	main()

