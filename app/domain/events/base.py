"""Базовый класс для доменных событий."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import ClassVar
from uuid import UUID, uuid4


@dataclass(frozen=True)
class BaseEvent:
    event_title: ClassVar[str]
    event_id: UUID = field(default_factory=uuid4, kw_only=True)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC), kw_only=True)
