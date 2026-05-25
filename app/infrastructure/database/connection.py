from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


async_engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)


async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
