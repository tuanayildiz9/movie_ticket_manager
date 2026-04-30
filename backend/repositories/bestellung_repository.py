from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlmodel import Session, delete, select

from backend.models import Bestellung, Ticket, TicketSnack, Verguensigungsart
from backend.models.orm.bestellung_sql import Bestellung as BestellungORM
from backend.models.orm.ticket_snack_sql import TicketSnack as TicketSnackORM
from backend.models.orm.ticket_sql import Ticket as TicketORM
from config.database import engine

from .bestellung_repository_interface import IBestellungRepository


class BestellungRepository(IBestellungRepository):
    def _to_domain(self, session: Session, row: BestellungORM) -> Bestellung:
        bestellung = Bestellung(
            bestellung_id=row.bestellung_id,
            kunde_id=row.kunde_id,
            bestellungsdatum=row.bestellungsdatum,
            anzahl_tickets=row.anzahl_tickets,
            total_betrag=row.total_betrag,
            tickets=[],
        )
        ticket_rows = session.exec(select(TicketORM).where(TicketORM.bestellung_id == row.bestellung_id)).all()
        for ticket_row in ticket_rows:
            ticket = Ticket(
                ticket_id=ticket_row.ticket_id,
                bestellung_id=ticket_row.bestellung_id,
                film_id=ticket_row.film_id,
                vorstellung_id=ticket_row.vorstellung_id,
                sitzplatz_id=ticket_row.sitzplatz_id,
                verguenstigungsart=Verguensigungsart(ticket_row.verguenstigungsart),
                preis=ticket_row.preis,
                snacks=[],
            )
            snack_rows = session.exec(select(TicketSnackORM).where(TicketSnackORM.ticket_id == ticket_row.ticket_id)).all()
            for snack_row in snack_rows:
                ticket.add_snack(
                    TicketSnack(ticket_id=snack_row.ticket_id, snack_id=snack_row.snack_id, anzahl=snack_row.anzahl)
                )
            bestellung.add_ticket(ticket)
        bestellung.anzahl_tickets = len(bestellung.tickets)
        return bestellung

    def _sync_tickets(self, session: Session, bestellung: Bestellung) -> None:
        for row in session.exec(select(TicketSnackORM).where(TicketSnackORM.ticket_id.in_(select(TicketORM.ticket_id).where(TicketORM.bestellung_id == bestellung.bestellung_id)))).all():
            session.delete(row)
        for row in session.exec(select(TicketORM).where(TicketORM.bestellung_id == bestellung.bestellung_id)).all():
            session.delete(row)

        for ticket in bestellung.tickets:
            ticket_row = TicketORM(
                ticket_id=ticket.ticket_id,
                bestellung_id=bestellung.bestellung_id,
                film_id=ticket.film_id,
                vorstellung_id=ticket.vorstellung_id,
                sitzplatz_id=ticket.sitzplatz_id,
                verguenstigungsart=ticket.verguenstigungsart.value,
                preis=ticket.preis,
            )
            session.add(ticket_row)
            session.flush()
            for snack_line in ticket.snacks:
                session.add(
                    TicketSnackORM(
                        ticket_id=ticket_row.ticket_id,
                        snack_id=snack_line.snack_id,
                        anzahl=snack_line.anzahl,
                    )
                )

    def create(self, bestellung: Bestellung) -> Bestellung:
        with Session(engine) as session:
            row = session.get(BestellungORM, bestellung.bestellung_id)
            if row is None:
                row = BestellungORM(
                    bestellung_id=bestellung.bestellung_id,
                    kunde_id=bestellung.kunde_id,
                    bestellungsdatum=bestellung.bestellungsdatum,
                    anzahl_tickets=bestellung.anzahl_tickets,
                    total_betrag=bestellung.total_betrag,
                )
                session.add(row)
            else:
                row.kunde_id = bestellung.kunde_id
                row.bestellungsdatum = bestellung.bestellungsdatum
                row.anzahl_tickets = bestellung.anzahl_tickets
                row.total_betrag = bestellung.total_betrag

            session.flush()
            self._sync_tickets(session, bestellung)
            session.commit()
            session.refresh(row)
            return self._to_domain(session, row)

    def get_by_id(self, bestellung_id: UUID) -> Bestellung | None:
        with Session(engine) as session:
            row = session.get(BestellungORM, bestellung_id)
            return self._to_domain(session, row) if row else None

    def list_by_kunde(self, kunde_id: UUID) -> list[Bestellung]:
        with Session(engine) as session:
            rows = session.exec(select(BestellungORM).where(BestellungORM.kunde_id == kunde_id)).all()
            return [self._to_domain(session, row) for row in rows]

    def list_by_film(self, film_id: UUID) -> list[Bestellung]:
        with Session(engine) as session:
            result = []
            for row in session.exec(select(BestellungORM)).all():
                order = self._to_domain(session, row)
                if any(ticket.film_id == film_id for ticket in order.tickets):
                    result.append(order)
            return result

    def list_by_vorstellung(self, vorstellung_id: UUID) -> list[Bestellung]:
        with Session(engine) as session:
            result = []
            for row in session.exec(select(BestellungORM)).all():
                order = self._to_domain(session, row)
                if any(ticket.vorstellung_id == vorstellung_id for ticket in order.tickets):
                    result.append(order)
            return result

    def list_all(self) -> list[Bestellung]:
        with Session(engine) as session:
            rows = session.exec(select(BestellungORM)).all()
            return [self._to_domain(session, row) for row in rows]
