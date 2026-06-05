"""Доменные события для пользователей."""

from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID

from app.domain.events.base import BaseEvent


@dataclass(frozen=True)
class UserCreatedEvent(BaseEvent):
    """Событие: создан новый пользователь."""

    event_title: ClassVar[str] = "user.created"
    user_id: UUID
    email: str
    firstname: str
    lastname: str


@dataclass(frozen=True)
class UserLoggedInEvent(BaseEvent):
    """Событие: пользователь вошел в систему."""

    event_title: ClassVar[str] = "user.logged_in"
    user_id: UUID
    email: str
    origin: str


@dataclass(frozen=True)
class UserUpdatedEvent(BaseEvent):
    """Событие: пользователь обновил свои данные."""

    event_title: ClassVar[str] = "user.updated"
    user_id: UUID
    firstname: str | None
    lastname: str | None
