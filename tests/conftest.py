from uuid import uuid4

import pytest
from faker import Faker

from app.domain.entities.user import User


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
