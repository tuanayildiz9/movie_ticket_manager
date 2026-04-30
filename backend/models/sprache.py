from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Sprache:
    sprache_id: UUID = field(default_factory=uuid4)
    name: str = ""

    def key(self) -> tuple[UUID]:
        return (self.sprache_id,)
