from abc import ABC, abstractmethod

from app.domain.events.base import BaseEvent


class IEventPublisher(ABC):
    @abstractmethod
    async def start(self) -> None:
        """Устанавливает соединение с брокером"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Закрывает соединение с брокером."""
        pass

    @abstractmethod
    async def publish(self, event: BaseEvent) -> None:
        """Публикует событие в брокер."""
        pass
