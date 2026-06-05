from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from faker import Faker
from pydantic import SecretStr

from app.application.services.user_service import UserService
from app.config import Settings
from app.domain.entities.user import User
from app.domain.repositories.users import IUserRepository


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
def user_service(mock_user_repo: IUserRepository) -> UserService:
    return UserService(mock_user_repo)


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
    )


@pytest.fixture(autouse=True)
def _override_settings(monkeypatch: pytest.MonkeyPatch, test_settings: Settings) -> None:
    monkeypatch.setattr("app.infrastructure.auth.jwt.settings", test_settings)
