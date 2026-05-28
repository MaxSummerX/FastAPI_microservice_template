from dataclasses import dataclass
from uuid import UUID


@dataclass
class User:
    id: UUID
    firstname: str
    lastname: str
    email: str

    def update_profile(self, firstname: str | None = None, lastname: str | None = None) -> None:
        if firstname:
            self.firstname = firstname
        if lastname:
            self.lastname = lastname
