from aiokafka.producer import AIOKafkaProducer

from app.config import settings
from app.infrastructure.message_brokers.kafka.publisher import KafkaEventPublisher
from app.infrastructure.message_brokers.protocols.publisher import IEventPublisher


_publisher: KafkaEventPublisher | None = None


def get_event_publisher() -> IEventPublisher:
    """Возвращает экземпляр KafkaEventPublisher."""
    global _publisher
    if _publisher is None:
        raise RuntimeError("Publisher is not initialized")
    return _publisher


async def init_publisher() -> None:
    """Инициализирует KafkaEventPublisher."""
    global _publisher
    producer = None
    try:
        producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_URL,
            enable_idempotence=settings.KAFKA_ENABLE_IDEMPOTENCE,
            acks=settings.KAFKA_ACKS,
        )
        publisher = KafkaEventPublisher(
            producer=producer,
            topic_mapping={
                "user.created": settings.USER_EVENTS_TOPIC,
                "user.updated": settings.USER_EVENTS_TOPIC,
                "user.logged_in": settings.USER_EVENTS_TOPIC,
            },
        )
        await publisher.start()
        _publisher = publisher
    except Exception:
        if producer is not None:
            await producer.stop()
        _publisher = None


async def close_publisher() -> None:
    """Закрывает KafkaEventPublisher."""
    global _publisher
    if _publisher is not None:
        await _publisher.stop()
        _publisher = None
