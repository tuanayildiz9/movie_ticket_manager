from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Bewertung:
    bewertung_id: UUID = field(default_factory=uuid4)
    kunde_id: UUID = field(default_factory=uuid4)
    film_id: UUID = field(default_factory=uuid4)
    bewertung: int = 0
    kommentar: str = ""
    bewertungsdatum: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not 1 <= self.bewertung <= 5:
            raise ValueError("Die Bewertung muss zwischen 1 und 5 liegen.")

    def is_positive(self) -> bool:
        return self.bewertung >= 4
