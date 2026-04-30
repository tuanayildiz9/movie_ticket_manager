from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class FilmlisteKunde:
    kunde_id: UUID = field(default_factory=uuid4)
    film_id: UUID = field(default_factory=uuid4)
    gespeichert_am: datetime = field(default_factory=datetime.utcnow)

    def key(self) -> tuple[UUID, UUID]:
        return self.kunde_id, self.film_id
