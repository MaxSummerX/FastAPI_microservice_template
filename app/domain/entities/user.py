"""Доменная сущность пользователя."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass
class User:
    id: UUID
    firstname: str
    lastname: str
    email: str
    oauth_provider: str
    oauth_id: str

    @classmethod
    def create_from_oauth(cls, email: str, firstname: str, lastname: str, oauth_provider: str, oauth_id: str) -> "User":
        """Создает пользователя из данных OAuth"""
        return cls(
            id=uuid4(),
            firstname=firstname,
            lastname=lastname,
            email=email,
            oauth_provider=oauth_provider,
            oauth_id=oauth_id,
        )

    def sync_from_oauth(self, email: str) -> None:
        """Синхронизирует email пользователя с OAuth"""
        self.email = email

    def update_profile(self, firstname: str | None = None, lastname: str | None = None) -> None:
        """Обновляет данные профиля пользователя. Только переданные значения будут обновлены."""
        if firstname:
            self.firstname = firstname
        if lastname:
            self.lastname = lastname
