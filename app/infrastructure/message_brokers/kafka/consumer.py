import logging
from collections.abc import AsyncGenerator
from dataclasses import fields
from datetime import datetime
from types import TracebackType
from typing import Self
from uuid import UUID

import orjson
from aiokafka import AIOKafkaConsumer

from app.domain.events.base import BaseEvent
from app.infrastructure.message_brokers.exception import UnknownEventError
from app.infrastructure.message_brokers.protocols.consumer import IEventConsumer


logger = logging.getLogger(__name__)


class KafkaEventConsumer(IEventConsumer):
    """Реализация consumer событий через Apache Kafka."""

    def __init__(self, consumer: AIOKafkaConsumer, event_mapping: dict[str, type[BaseEvent]]):
        self.consumer = consumer
        self.event_mapping = event_mapping

    async def start(self) -> None:
        await self.consumer.start()

    async def stop(self) -> None:
        await self.consumer.stop()

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.stop()

    def subscribe(self, topic: str) -> AsyncGenerator[BaseEvent]:
        self.consumer.subscribe([topic])
        return self._message_generator()

    async def ack(self) -> None:
        await self.consumer.commit()

    async def _message_generator(self) -> AsyncGenerator[BaseEvent]:
        """Асинхронный генератор: читает сообщения и десериализует в доменные события."""
        async for message in self.consumer:
            if message.value is None:
                continue
            try:
                data = orjson.loads(message.value)
                yield self._from_dict(data)
            except (UnknownEventError, orjson.JSONDecodeError) as e:
                logger.warning("Пропущено битое сообщение: %s", e)
                await self.consumer.commit()

    def _from_dict(self, data: dict) -> BaseEvent:
        """Десериализует словарь в доменное событие по event_title."""
        event_title = data.pop("event_title", "")
        event_cls = self.event_mapping.get(event_title, None)
        if event_cls is None:
            raise UnknownEventError(f"Unknown event: {event_title}")
        type_hints = {f.name: f.type for f in fields(event_cls)}
        for key, value in data.items():
            if key not in type_hints:
                continue
            hint = type_hints[key]
            if hint is UUID and isinstance(value, str):
                data[key] = UUID(value)
            elif hint is datetime and isinstance(value, str):
                data[key] = datetime.fromisoformat(value)
        return event_cls(**data)
