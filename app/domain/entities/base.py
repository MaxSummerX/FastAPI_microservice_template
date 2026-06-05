"""Базовая сущность для всех доменных объектов."""

from copy import copy
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from app.domain.events.base import BaseEvent


@dataclass
class BaseEntity:
    id: UUID = field(default_factory=uuid4, kw_only=True)

    _events: list[BaseEvent] = field(default_factory=list, kw_only=True)

    def register_event(self, event: BaseEvent) -> None:
        """Зарегистрировать доменное событие."""
        self._events.append(event)

    def pull_events(self) -> list[BaseEvent]:
        """Извлечь все зарегистрированные события и очистить список."""
        registered_events = copy(self._events)

        self._events.clear()
        return registered_events
