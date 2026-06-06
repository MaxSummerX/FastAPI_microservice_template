from dataclasses import asdict
from uuid import UUID

import orjson
from aiokafka.producer import AIOKafkaProducer

from app.domain.events.base import BaseEvent
from app.infrastructure.message_brokers.protocols.publisher import IEventPublisher


class KafkaEventPublisher(IEventPublisher):
    """Реализация публикации событий через Apache Kafka."""

    def __init__(self, producer: AIOKafkaProducer, topic_mapping: dict[str, str]):
        self.producer = producer
        self.topic_mapping = topic_mapping

    async def start(self) -> None:
        await self.producer.start()

    async def stop(self) -> None:
        await self.producer.stop()

    async def publish(self, event: BaseEvent) -> None:
        topic: str = self.topic_mapping[event.event_title]
        value: bytes = orjson.dumps(self._to_dict(event))
        key: bytes = event.routing_key.encode("utf-8")
        await self.producer.send_and_wait(topic=topic, value=value, key=key)

    def _to_dict(self, event: BaseEvent) -> dict:
        """Преобразует событие в словарь для публикации в Kafka."""
        data = asdict(event)
        data["event_title"] = event.event_title
        for key, value in data.items():
            if isinstance(value, UUID):
                data[key] = str(value)
        return data
