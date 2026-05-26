from datetime import datetime
from uuid import UUID

from backend.models import Bestellung, Ticket, TicketSnack, Verguensigungsart

from backend.repositories.bestellung_repository import BestellungRepository
from backend.repositories.film_repository import FilmRepository
from backend.repositories.snack_repository import SnackRepository
from backend.repositories.kunde_repository import KundeRepository


class BestellungService:
    def __init__(
        self,
        bestellung_repo: BestellungRepository,
        film_repo: FilmRepository,
        kunde_repo: KundeRepository,
        snack_repo: SnackRepository,
    ) -> None:
        self.bestellung_repo = bestellung_repo
        self.film_repo = film_repo
        self.kunde_repo = kunde_repo
        self.snack_repo = snack_repo

    def create_order(
        self,
        kunde_id: UUID,
        tickets: list[dict[str, object]],
        snacks: list[dict[str, object]] | None = None,
        payment: dict[str, object] | None = None,
    ) -> Bestellung:
        kunde = self.kunde_repo.get_by_id(kunde_id)
        if kunde is None:
            raise ValueError("Kunde wurde nicht gefunden.")

        bestellung = Bestellung(kunde_id=kunde_id)
        created_tickets: list[Ticket] = []

        for ticket_data in tickets:
            film_id = ticket_data.get("film_id")
            vorstellung_id = ticket_data.get("vorstellung_id")
            sitzplatz_id = ticket_data.get("sitzplatz_id")
            if not isinstance(film_id, UUID) or not isinstance(vorstellung_id, UUID) or not isinstance(sitzplatz_id, UUID):
                raise ValueError("Ticketdaten sind unvollständig.")

            film = self.film_repo.get_by_id(film_id)
            if film is None:
                raise ValueError("Film wurde nicht gefunden.")

            if not self.film_repo.reserve_seat(vorstellung_id, sitzplatz_id):
                raise ValueError("Sitzplatz konnte nicht reserviert werden.")

            # Geschäftsregel: Keine Buchung für Vorstellungen in der Vergangenheit
            vorstellung = self.film_repo.get_vorstellung_by_id(vorstellung_id)
            if vorstellung and getattr(vorstellung, "startzeit", None) is not None:
                if vorstellung.startzeit < datetime.utcnow():
                    raise ValueError("Buchung für vergangene Vorstellungen ist nicht möglich.")

            raw_discount = ticket_data.get("verguenstigungsart", Verguensigungsart.REGULAER)
            if isinstance(raw_discount, Verguensigungsart):
                discount_type = raw_discount
            else:
                discount_type = Verguensigungsart(str(raw_discount).lower())

            # Geschäftsregel: Für Filme mit Altersfreigabe >= 16 sind Kindervergünstigungen
            # nicht zulässig (Kinder zählen bis 15 Jahre).
            if discount_type == Verguensigungsart.KIND and getattr(film, "altersfreigabe", 0) >= 16:
                raise ValueError("Kindervergünstigung ist für Filme ab 16 nicht erlaubt.")

            ticket = Ticket(
                bestellung_id=bestellung.bestellung_id,
                film_id=film_id,
                vorstellung_id=vorstellung_id,
                sitzplatz_id=sitzplatz_id,
                verguenstigungsart=discount_type,
            )
            ticket.apply_discount(film.basispreis)
            bestellung.add_ticket(ticket)
            created_tickets.append(ticket)

        if snacks:
            for snack_data in snacks:
                ticket_index = int(snack_data.get("ticket_index", 0))
                snack_id = snack_data.get("snack_id")
                anzahl = int(snack_data.get("anzahl", 1))
                if not isinstance(snack_id, UUID):
                    raise ValueError("Snackdaten sind unvollständig.")
                if not 0 <= ticket_index < len(created_tickets):
                    raise ValueError("Ungültiger Ticket-Index für Snacks.")
                snack = self.snack_repo.get_by_id(snack_id)
                if snack is None:
                    raise ValueError("Snack wurde nicht gefunden.")
                ticket_snack = TicketSnack(ticket_id=created_tickets[ticket_index].ticket_id, snack_id=snack_id, anzahl=anzahl)
                created_tickets[ticket_index].add_snack(ticket_snack)

        snack_prices = {snack.snack_id: snack.preis for snack in self.snack_repo.list_all()}
        bestellung.calculate_total(snack_prices=snack_prices)
        self.bestellung_repo.create(bestellung)
        return bestellung

    def get_order_summary(self, bestellung_id: UUID, film_titel: str, saal: str, ort: str, uhrzeit: datetime) -> dict[str, object]:
        bestellung = self.bestellung_repo.get_by_id(bestellung_id)
        if bestellung is None:
            raise ValueError("Bestellung wurde nicht gefunden.")
        return bestellung.summary(film_titel=film_titel, saal=saal, ort=ort, uhrzeit=uhrzeit)

    def available_seats(self, vorstellung_id: UUID) -> list[dict[str, object]]:
        seats = self.film_repo.list_available_seats(vorstellung_id)
        return [
            {
                "sitzplatz_id": seat.sitzplatz_id,
                "sitz_label": seat.sitz_label,
                "sektor": seat.sektor,
            }
            for seat in seats
        ]
