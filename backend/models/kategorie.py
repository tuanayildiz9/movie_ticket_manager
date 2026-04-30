from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Kategorie:
    kategorie_id: UUID = field(default_factory=uuid4)
    name: str = ""

    def key(self) -> tuple[UUID]:
        return (self.kategorie_id,)
