from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class FilmSprache:
    film_id: UUID = field(default_factory=uuid4)
    sprache_id: UUID = field(default_factory=uuid4)

    def key(self) -> tuple[UUID, UUID]:
        return self.film_id, self.sprache_id
