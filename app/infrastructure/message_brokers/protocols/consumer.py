from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from app.domain.events.base import BaseEvent


class IEventConsumer(ABC):
    @abstractmethod
    async def start(self) -> None:
        """Установить соединение с брокером и начать чтение."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Остановить чтение и закрыть соединение."""
        pass

    @abstractmethod
    def subscribe(self, topic: str) -> AsyncGenerator[BaseEvent]:
        """Подписаться на топик."""
        pass

    @abstractmethod
    async def ack(self) -> None:
        """Подтвердить обработку события."""
        pass
