from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from .common import to_decimal


@dataclass
class TicketSnack:
    ticket_id: UUID = field(default_factory=uuid4)
    snack_id: UUID = field(default_factory=uuid4)
    anzahl: int = 1

    def line_total(self, snack_price: Decimal) -> Decimal:
        return to_decimal(snack_price) * self.anzahl
