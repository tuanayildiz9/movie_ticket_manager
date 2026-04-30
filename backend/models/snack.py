from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from .common import to_decimal


@dataclass
class Snack:
    snack_id: UUID = field(default_factory=uuid4)
    name: str = ""
    preis: Decimal = Decimal("0.00")

    def total_price(self, quantity: int = 1) -> Decimal:
        return to_decimal(self.preis) * quantity
