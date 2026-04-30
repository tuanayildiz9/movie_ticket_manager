from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Sitzplatz:
    sitzplatz_id: UUID = field(default_factory=uuid4)
    sitz_label: str = ""
    sektor: str = ""
    besetzt: bool = False
    vorstellung_id: UUID | None = None

    def reserve(self) -> bool:
        if self.besetzt:
            return False
        self.besetzt = True
        return True

    def release(self) -> None:
        self.besetzt = False

    def is_available(self) -> bool:
        return not self.besetzt

    def assign_to_vorstellung(self, vorstellung_id: UUID) -> None:
        self.vorstellung_id = vorstellung_id
