from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class KundenKategoriePraeferenz:
    kunde_id: UUID = field(default_factory=uuid4)
    kategorie_id: UUID = field(default_factory=uuid4)

    def key(self) -> tuple[UUID, UUID]:
        return self.kunde_id, self.kategorie_id
