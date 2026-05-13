from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from .common import to_decimal
from .enums import Verguensigungsart
from .ticket_snack import TicketSnack


@dataclass
class Ticket:
    ticket_id: UUID = field(default_factory=uuid4)
    bestellung_id: UUID = field(default_factory=uuid4)
    film_id: UUID = field(default_factory=uuid4)
    vorstellung_id: UUID = field(default_factory=uuid4)
    sitzplatz_id: UUID = field(default_factory=uuid4)
    verguenstigungsart: Verguensigungsart = Verguensigungsart.REGULAER
    preis: Decimal = Decimal("0.00")
    snacks: list[TicketSnack] = field(default_factory=list)

    def apply_discount(self, base_price: Decimal | int | float | str) -> Decimal:
        discount_amounts = {
            Verguensigungsart.REGULAER: Decimal("0.00"),
            Verguensigungsart.STUDENT: Decimal("4.00"),
            Verguensigungsart.SENIOR: Decimal("3.00"),
            Verguensigungsart.KIND: Decimal("6.00"),
        }
        base = to_decimal(base_price)
        discount = discount_amounts.get(self.verguenstigungsart, Decimal("0.00"))
        self.preis = max(base - discount, Decimal("0.00")).quantize(Decimal("0.01"))
        return self.preis

    def add_snack(self, snack_line: TicketSnack) -> None:
        self.snacks.append(snack_line)

    def calculate_total(self, snack_prices: dict[UUID, Decimal] | None = None) -> Decimal:
        total = to_decimal(self.preis)
        if snack_prices:
            for snack_line in self.snacks:
                snack_price = snack_prices.get(snack_line.snack_id)
                if snack_price is not None:
                    total += snack_line.line_total(snack_price)
        return total.quantize(Decimal("0.01"))
