from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from .sitzplatz import Sitzplatz


@dataclass
class Vorstellung:
    vorstellung_id: UUID = field(default_factory=uuid4)
    film_id: UUID = field(default_factory=uuid4)
    saal: str = ""
    ort: str = ""
    startzeit: datetime = field(default_factory=datetime.utcnow)
    endzeit: datetime | None = None
    sitzplaetze: list[Sitzplatz] = field(default_factory=list)

    def available_seats(self) -> list[Sitzplatz]:
        return [seat for seat in self.sitzplaetze if seat.is_available()]

    def free_seat_count(self) -> int:
        return len(self.available_seats())

    def reserve_seat(self, sitzplatz_id: UUID) -> bool:
        for sitzplatz in self.sitzplaetze:
            if sitzplatz.sitzplatz_id == sitzplatz_id:
                sitzplatz.assign_to_vorstellung(self.vorstellung_id)
                return sitzplatz.reserve()
        return False

    def release_seat(self, sitzplatz_id: UUID) -> bool:
        for sitzplatz in self.sitzplaetze:
            if sitzplatz.sitzplatz_id == sitzplatz_id:
                sitzplatz.release()
                return True
        return False

    def sold_ticket_count(self) -> int:
        return sum(1 for seat in self.sitzplaetze if seat.besetzt)
