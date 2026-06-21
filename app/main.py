import logging
from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.cache.redis.factories import create_cache
from app.infrastructure.database.dependencies import get_db
from app.infrastructure.logging import setup_logging
from app.infrastructure.message_brokers.kafka.factories import create_publisher
from app.presentation.routers import auth, demo, users


setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    async with AsyncExitStack() as stack:
        logger.info("Запуск cache")
        cache = create_cache()
        await cache.start()
        stack.push_async_callback(cache.stop)
        app.state.cache = cache
        logger.info("Cache запущен")

        logger.info("Запуск publisher")
        publisher = create_publisher()
        await publisher.start()
        stack.push_async_callback(publisher.stop)
        app.state.publisher = publisher
        logger.info("Publisher запущен")

        try:
            yield
        finally:
            logger.info("Завершение работы приложения")
    logger.info("Работа приложения завершена")


app = FastAPI(title="User-service", version="0.1.0", lifespan=lifespan)


app.include_router(users.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

# Демо-роутер для демонстрации consumer-group
app.include_router(demo.router, prefix="/api/v1")


@app.get("/health_check", tags=["Health Check"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/readiness_check", tags=["Readiness Check"])
async def readiness_check(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=500, detail="Database is not available") from None
    return {"status": "ready"}


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {"status": "Hello from User-service"}
