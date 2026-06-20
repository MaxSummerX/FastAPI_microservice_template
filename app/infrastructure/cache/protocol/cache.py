from abc import ABC, abstractmethod


class ICache(ABC):
    @abstractmethod
    async def get(self, key: str) -> str | None:
        """Получение значения по ключу из кэша"""
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """Записать значение по ключу в кэш (с опциональным TTL, в секундах)."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Удаление значения по ключу из кэша"""
        pass
