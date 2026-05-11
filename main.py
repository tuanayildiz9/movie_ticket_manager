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


def main() -> None:
	seed_database()
	user_service, film_service, bestellung_service, admin_service = build_application()

	print("Movie Ticket Manager ist gestartet.")
	print(f"Verfuegbare Services: {user_service.__class__.__name__}, {film_service.__class__.__name__}, {bestellung_service.__class__.__name__}, {admin_service.__class__.__name__}")


if __name__ == "__main__":
	main()

