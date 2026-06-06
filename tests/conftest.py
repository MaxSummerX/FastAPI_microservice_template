from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import jwt
import pytest
import pytest_asyncio
from faker import Faker
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.application.services.user_service import UserService
from app.config import Settings
from app.domain.entities.user import User
from app.domain.repositories.users import IUserRepository
from app.infrastructure.database.dependencies import get_db
from app.infrastructure.message_brokers.kafka.dependencies import get_event_publisher
from app.infrastructure.message_brokers.protocols.publisher import IEventPublisher
from app.infrastructure.persistence.models import User as UserModel
from app.infrastructure.persistence.models.base_model import Base
from app.infrastructure.persistence.sqlalchemy.user_repository import UserSQLAlchemyRepository
from app.main import app


@pytest.fixture
def example_user(faker: Faker) -> User:

    return User(
        id=uuid4(),
        email=faker.email(),
        firstname=faker.first_name(),
        lastname=faker.last_name(),
        oauth_provider="google",
        oauth_id=faker.numerify("#" * 21),
    )


@pytest.fixture
def mock_user_repo() -> AsyncMock:
    repo = AsyncMock(spec=IUserRepository)
    return repo


@pytest.fixture
def mock_event_publisher() -> AsyncMock:
    publisher = AsyncMock(spec=IEventPublisher)
    return publisher


@pytest.fixture
def user_service(mock_user_repo: IUserRepository, mock_event_publisher: IEventPublisher) -> UserService:
    return UserService(mock_user_repo, mock_event_publisher)


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings(
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        SECRET_KEY=SecretStr("test-secret-key-that-is-at-least-32-bytes-long!"),
        ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=30,
        REFRESH_TOKEN_EXPIRE_DAYS=7,
        DEBUG=True,
        GOOGLE_CLIENT_ID="test-client-id",
        GOOGLE_CLIENT_SECRET=SecretStr("test-client-secret"),
        GOOGLE_REDIRECT_URI="http://localhost:8000/api/v1/auth/google/callback",
        KAFKA_URL="localhost:9092",
        USER_EVENTS_TOPIC="user.events",
    )


@pytest.fixture(autouse=True)
def _override_settings(monkeypatch: pytest.MonkeyPatch, test_settings: Settings) -> None:
    monkeypatch.setattr("app.infrastructure.auth.jwt.settings", test_settings)


@pytest_asyncio.fixture(scope="session")
async def test_db_engine(test_settings: Settings) -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(test_settings.DATABASE_URL, echo=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def test_session_factory(test_db_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(test_db_engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def test_db_session(test_session_factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession]:
    async with test_session_factory() as session:
        await session.execute(delete(UserModel))
        await session.commit()
        await session.begin()
        yield session
        if session.is_active:
            await session.rollback()


@pytest_asyncio.fixture
async def test_client(test_db_session: AsyncSession, mock_event_publisher: AsyncMock) -> AsyncGenerator[AsyncClient]:

    app.dependency_overrides[get_db] = lambda: test_db_session
    app.dependency_overrides[get_event_publisher] = lambda: mock_event_publisher
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def db_user(test_db_session: AsyncSession, faker: Faker) -> User:
    user = User.create_from_oauth(
        email=faker.email(),
        firstname=faker.first_name(),
        lastname=faker.last_name(),
        oauth_provider="google",
        oauth_id=faker.numerify("#" * 21),
    )
    repo = UserSQLAlchemyRepository(test_db_session)
    await repo.create(user)
    return user


@pytest_asyncio.fixture
async def other_db_user(test_db_session: AsyncSession, faker: Faker) -> User:
    user = User.create_from_oauth(
        email=faker.email(),
        firstname=faker.first_name(),
        lastname=faker.last_name(),
        oauth_provider="google",
        oauth_id=faker.numerify("#" * 21),
    )
    repo = UserSQLAlchemyRepository(test_db_session)
    await repo.create(user)
    return user


@pytest.fixture
def auth_headers(test_settings: Settings, db_user: User) -> dict[str, str]:
    expire = datetime.now(UTC) + timedelta(minutes=30)
    payload = {"sub": str(db_user.id), "email": db_user.email, "exp": expire}
    token = jwt.encode(payload, key=test_settings.SECRET_KEY.get_secret_value(), algorithm=test_settings.ALGORITHM)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_user_auth_headers(test_settings: Settings, other_db_user: User) -> dict[str, str]:
    expire = datetime.now(UTC) + timedelta(minutes=30)
    payload = {"sub": str(other_db_user.id), "email": other_db_user.email, "exp": expire}
    token = jwt.encode(payload, key=test_settings.SECRET_KEY.get_secret_value(), algorithm=test_settings.ALGORITHM)
    return {"Authorization": f"Bearer {token}"}
