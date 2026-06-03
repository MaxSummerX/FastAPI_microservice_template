from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from faker import Faker

from app.application.services.user_service import UserService
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
