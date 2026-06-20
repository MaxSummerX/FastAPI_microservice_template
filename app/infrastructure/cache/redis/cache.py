from typing import cast

from redis.asyncio import Redis

from app.infrastructure.cache.protocol.cache import ICache


class RedisCache(ICache):
    """Реализация кэша на основе Redis."""

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def start(self) -> None:
        await self.redis_client.ping()  # type: ignore[misc]

    async def stop(self) -> None:
        await self.redis_client.aclose()

    async def get(self, key: str) -> str | None:
        return cast(str | None, await self.redis_client.get(key))

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        await self.redis_client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self.redis_client.delete(key)
