from dataclasses import dataclass
from uuid import UUID


@dataclass
class User:
    id: UUID
    firstname: str
    lastname: str
    email: str
