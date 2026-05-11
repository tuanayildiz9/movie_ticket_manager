from dataclasses import dataclass, field
from hashlib import sha256
from uuid import UUID, uuid4


@dataclass
class Account:
    account_id: UUID = field(default_factory=uuid4)
    email: str = ""
    passwort_hash: str = ""
    rolle: str = "kunde"
    aktiv: bool = True

    def set_password(self, plain_password: str) -> None:
        self.passwort_hash = sha256(plain_password.encode("utf-8")).hexdigest()

    def check_password(self, plain_password: str) -> bool:
        return self.passwort_hash == sha256(plain_password.encode("utf-8")).hexdigest()

    def is_admin(self) -> bool:
        return self.rolle == "admin"