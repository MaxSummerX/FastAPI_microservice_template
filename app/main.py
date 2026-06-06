from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.dependencies import get_db
from app.infrastructure.message_brokers.kafka.dependencies import close_publisher, init_publisher
from app.presentation.routers import auth, users


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    await init_publisher()
    yield
    await close_publisher()


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
