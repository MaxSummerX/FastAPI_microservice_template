import asyncio

from app.infrastructure.logging import setup_consumer_file_log, setup_logging
from app.infrastructure.message_brokers.kafka.factories import create_consumer
from app.presentation.event_dispatcher import dispatcher, process_events
from app.presentation.handlers import register_handlers


setup_logging()
register_handlers()
setup_consumer_file_log()


async def main() -> None:
    """Запуск worker: подключаемся к Kafka и начинаем обработку событий."""
    async with create_consumer() as consumer:
        await process_events(consumer, dispatcher)


if __name__ == "__main__":
    asyncio.run(main())
