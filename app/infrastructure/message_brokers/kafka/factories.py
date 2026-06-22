from uuid import uuid4

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.config import settings
from app.domain.events.base import BaseEvent
from app.domain.events.users import UserCreatedEvent, UserLoggedInEvent, UserUpdatedEvent
from app.infrastructure.message_brokers.kafka.consumer import KafkaEventConsumer
from app.infrastructure.message_brokers.kafka.publisher import KafkaEventPublisher


_event_map: dict[str, type[BaseEvent]] = {
    "user.created": UserCreatedEvent,
    "user.logged_in": UserLoggedInEvent,
    "user.updated": UserUpdatedEvent,
}

_topic_mapping: dict[str, str] = {
    "user.created": settings.USER_EVENTS_TOPIC,
    "user.updated": settings.USER_EVENTS_TOPIC,
    "user.logged_in": settings.USER_EVENTS_TOPIC,
}


def create_publisher() -> KafkaEventPublisher:
    """Создать экземпляр Kafka-паблишера для публикации доменных событий"""
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_URL,
        enable_idempotence=settings.KAFKA_ENABLE_IDEMPOTENCE,
        acks=settings.KAFKA_ACKS,
    )
    return KafkaEventPublisher(producer=producer, topic_mapping=_topic_mapping)


def create_consumer() -> KafkaEventConsumer:
    """Создать экземпляр Kafka-консьюмера для обработки входящих событий."""
    consumer = AIOKafkaConsumer(
        bootstrap_servers=settings.KAFKA_URL,
        group_id=settings.KAFKA_CONSUMER_GROUP,
        client_id=f"consumer-{uuid4().hex[:8]}",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )
    return KafkaEventConsumer(
        consumer=consumer,
        event_mapping=_event_map,
    )
