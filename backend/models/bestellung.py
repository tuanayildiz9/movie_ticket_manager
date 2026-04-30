from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from .common import to_decimal
from .ticket import Ticket


@dataclass
class Bestellung:
    bestellung_id: UUID = field(default_factory=uuid4)
    kunde_id: UUID = field(default_factory=uuid4)
    bestellungsdatum: datetime = field(default_factory=datetime.utcnow)
    anzahl_tickets: int = 0
    total_betrag: Decimal = Decimal("0.00")
    tickets: list[Ticket] = field(default_factory=list)

    def add_ticket(self, ticket: Ticket) -> None:
        self.tickets.append(ticket)
        self.anzahl_tickets = len(self.tickets)

    def calculate_total(self, snack_prices: dict[UUID, Decimal] | None = None) -> Decimal:
        total = Decimal("0.00")
        for ticket in self.tickets:
            total += to_decimal(ticket.preis)
            if snack_prices:
                for snack_line in ticket.snacks:
                    snack_price = snack_prices.get(snack_line.snack_id)
                    if snack_price is not None:
                        total += snack_line.line_total(snack_price)
        self.total_betrag = total.quantize(Decimal("0.01"))
        return self.total_betrag

    def summary(self, film_titel: str, saal: str, ort: str, uhrzeit: datetime) -> dict[str, Any]:
        return {
            "bestellung_id": self.bestellung_id,
            "kunde_id": self.kunde_id,
            "film_titel": film_titel,
            "saal": saal,
            "ort": ort,
            "uhrzeit": uhrzeit,
            "anzahl_tickets": self.anzahl_tickets,
            "total_betrag": self.total_betrag,
        }
