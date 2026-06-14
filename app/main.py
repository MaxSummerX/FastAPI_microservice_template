import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.dependencies import get_db
from app.infrastructure.logging import setup_consumer_file_log, setup_logging
from app.infrastructure.message_brokers.kafka.factories import create_consumer, create_publisher
from app.presentation.event_dispatcher import dispatcher, process_events
from app.presentation.handlers import register_handlers
from app.presentation.routers import auth, users


setup_logging()
setup_consumer_file_log()
register_handlers()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    logger.info("Запуск publisher")
    publisher = create_publisher()
    await publisher.start()
    app.state.publisher = publisher
    logger.info("Publisher запущен")

    try:
        logger.info("Запуск consumer")
        async with create_consumer() as consumer:
            task = asyncio.create_task(process_events(consumer, dispatcher), name="event_consumer")
            logger.info("Consumer запущен")
            logger.info("Приложение запущено")
            try:
                yield
            finally:
                logger.info("Завершение работы приложения")
                logger.info("Остановка consumer")
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                logger.info("Consumer остановлен")

    finally:
        await publisher.stop()
        logger.info("Publisher остановлен")
        logger.info("Работа приложения завершена")


app = FastAPI(title="User-service", version="0.1.0", lifespan=lifespan)


app.include_router(users.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")


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
