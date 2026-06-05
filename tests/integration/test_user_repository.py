import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.infrastructure.persistence.sqlalchemy.user_repository import UserSQLAlchemyRepository


@pytest.mark.asyncio
async def test_create_and_get_by_id(test_db_session: AsyncSession, example_user: User) -> None:
    """Проверяет, что create сохраняет пользователя, а get_by_id находит его."""
    repo = UserSQLAlchemyRepository(test_db_session)

    await repo.create(example_user)
    user = await repo.get_by_id(example_user.id)

    assert user is not None
    assert user.id == example_user.id
    assert user.email == example_user.email
    assert user.firstname == example_user.firstname
    assert user.lastname == example_user.lastname
    assert user.oauth_provider == example_user.oauth_provider
    assert user.oauth_id == example_user.oauth_id


@pytest.mark.asyncio
async def test_get_by_id_not_found(test_db_session: AsyncSession) -> None:
    """Проверяет, что get_by_id возвращает None для несуществующего id."""
    from uuid import uuid4

    repo = UserSQLAlchemyRepository(test_db_session)

    user = await repo.get_by_id(uuid4())

    assert user is None


@pytest.mark.asyncio
async def test_get_by_email(test_db_session: AsyncSession, example_user: User) -> None:
    """Проверяет, что get_by_email находит пользователя по email."""
    repo = UserSQLAlchemyRepository(test_db_session)

    await repo.create(example_user)
    user = await repo.get_by_email(example_user.email)

    assert user is not None
    assert user.id == example_user.id
    assert user.email == example_user.email


@pytest.mark.asyncio
async def test_get_by_email_not_found(test_db_session: AsyncSession, faker: Faker) -> None:
    """Проверяет, что get_by_email возвращает None для несуществующего email."""
    repo = UserSQLAlchemyRepository(test_db_session)

    user = await repo.get_by_email(faker.email())

    assert user is None


@pytest.mark.asyncio
async def test_get_by_oauth(test_db_session: AsyncSession, example_user: User) -> None:
    """Проверяет, что get_by_oauth находит пользователя по provider + oauth_id."""
    repo = UserSQLAlchemyRepository(test_db_session)

    await repo.create(example_user)
    user = await repo.get_by_oauth(example_user.oauth_provider, example_user.oauth_id)

    assert user is not None
    assert user.id == example_user.id
    assert user.oauth_provider == example_user.oauth_provider
    assert user.oauth_id == example_user.oauth_id


@pytest.mark.asyncio
async def test_get_by_oauth_not_found(test_db_session: AsyncSession, faker: Faker) -> None:
    """Проверяет, что get_by_oauth возвращает None для несуществующего OAuth."""
    repo = UserSQLAlchemyRepository(test_db_session)

    user = await repo.get_by_oauth("google", faker.numerify("#" * 21))

    assert user is None


@pytest.mark.asyncio
async def test_save(test_db_session: AsyncSession, example_user: User, faker: Faker) -> None:
    """Проверяет, что save обновляет поля пользователя в БД."""
    repo = UserSQLAlchemyRepository(test_db_session)

    await repo.create(example_user)

    new_firstname = faker.first_name()
    new_lastname = faker.last_name()
    example_user.update_profile(firstname=new_firstname, lastname=new_lastname)

    saved = await repo.save(example_user)

    user = await repo.get_by_id(example_user.id)

    assert saved.firstname == new_firstname
    assert saved.lastname == new_lastname
    assert user is not None
    assert user.firstname == new_firstname
    assert user.lastname == new_lastname
