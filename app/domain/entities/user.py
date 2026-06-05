"""Доменная сущность пользователя."""

from dataclasses import dataclass

from app.domain.entities.base import BaseEntity
from app.domain.events.users import UserCreatedEvent, UserUpdatedEvent


@dataclass
class User(BaseEntity):
    firstname: str
    lastname: str
    email: str
    oauth_provider: str
    oauth_id: str

    @classmethod
    def create_from_oauth(cls, email: str, firstname: str, lastname: str, oauth_provider: str, oauth_id: str) -> "User":
        """
        Создает пользователя из данных OAuth.
        Зарегистрирует событие UserCreatedEvent.
        """
        user = cls(
            firstname=firstname,
            lastname=lastname,
            email=email,
            oauth_provider=oauth_provider,
            oauth_id=oauth_id,
        )
        user.register_event(
            UserCreatedEvent(
                user_id=user.id,
                email=user.email,
                firstname=user.firstname,
                lastname=user.lastname,
            )
        )
        return user

    def sync_from_oauth(self, email: str) -> None:
        """Синхронизирует email пользователя с OAuth"""
        self.email = email

    def update_profile(self, firstname: str | None = None, lastname: str | None = None) -> None:
        """
        Обновляет данные профиля пользователя.
        Только переданные значения будут обновлены.
        Зарегистрирует событие UserUpdatedEvent.
        """
        if not firstname and not lastname:
            return

        if firstname:
            self.firstname = firstname
        if lastname:
            self.lastname = lastname
        self.register_event(
            UserUpdatedEvent(
                user_id=self.id,
                firstname=self.firstname,
                lastname=self.lastname,
            )
        )
