from abc import ABC, abstractmethod

from app.domain.events.base import BaseEvent


class IEventPublisher(ABC):
    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass

    @abstractmethod
    async def publish(self, event: BaseEvent) -> None:
        pass
