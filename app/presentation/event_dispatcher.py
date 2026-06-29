import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

from app.config import settings
from app.domain.events.base import BaseEvent
from app.infrastructure.message_brokers.protocols.consumer import IEventConsumer


logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseEvent)


class HandlerNotFoundError(Exception):
    pass


class EventDispatcher:
    """Маршрутизатор доменных событий по зарегистрированным обработчикам."""

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[BaseEvent], Awaitable[None]]] = {}

    def register(self, event_type: str, handler: Callable[[T], Awaitable[None]]) -> None:
        """Зарегистрировать обработчик для события."""
        self._handlers[event_type] = handler  # type: ignore[assignment]

    async def dispatch(self, event: BaseEvent) -> None:
        """Найти обработчик по `event.event_title` и вызвать его."""
        handler = self._handlers.get(event.event_title)
        if not handler:
            raise HandlerNotFoundError(event.event_title)
        await handler(event)


async def process_events(consumer: IEventConsumer, router: EventDispatcher) -> None:
    """Бесконечный цикл чтения событий из брокера и их диспетчеризации."""
    async for event in consumer.subscribe(settings.USER_EVENTS_TOPIC):
        try:
            await router.dispatch(event)
            await consumer.ack()
        except HandlerNotFoundError:
            logger.warning("Нет обработчика для события: %s", event.event_title)
            # делаем commit что сообщение обработано, чтобы не зацикливаться на отсутствии обработчика
            await consumer.ack()
        except Exception as e:
            logger.error("Ошибка при обработке события %s: %s", event.event_title, e)
            await consumer.ack()


dispatcher = EventDispatcher()
