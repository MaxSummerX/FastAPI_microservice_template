from redis.asyncio import Redis as AsyncRedis

from app.config import settings
from app.infrastructure.cache.redis.cache import RedisCache


def create_cache() -> RedisCache:
    """Создать экземпляр кэша на Redis."""
    redis_client = AsyncRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD.get_secret_value(),
        decode_responses=True,
    )
    return RedisCache(redis_client=redis_client)
