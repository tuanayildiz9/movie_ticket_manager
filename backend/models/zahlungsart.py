from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Zahlungsart:
    zahlungsart_id: UUID = field(default_factory=uuid4)
    name: str = ""

    def __str__(self) -> str:
        return self.name or "Zahlungsart"
