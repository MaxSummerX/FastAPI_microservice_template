from unittest.mock import AsyncMock

import pytest
from faker import Faker

from app.application.exception import UserNotFoundException
from app.application.services.user_service import UserService
from app.domain.entities.user import User


@pytest.mark.asyncio
async def test_get_by_id_found(user_service: UserService, mock_user_repo: AsyncMock, example_user: User) -> None:
    """Проверяет, что get_by_id возвращает пользователя при найденном id."""
    mock_user_repo.get_by_id.return_value = example_user
    result = await user_service.get_by_id(example_user.id)

    assert result == example_user
    mock_user_repo.get_by_id.assert_called_once_with(example_user.id)


@pytest.mark.asyncio
async def test_get_by_id_not_found(user_service: UserService, mock_user_repo: AsyncMock, example_user: User) -> None:
    """Проверяет, что get_by_id выбрасывает исключение при не найденном id."""
    mock_user_repo.get_by_id.return_value = None

    with pytest.raises(UserNotFoundException):
        await user_service.get_by_id(example_user.id)


@pytest.mark.asyncio
async def test_get_by_email_found(user_service: UserService, mock_user_repo: AsyncMock, example_user: User) -> None:
    """Проверяет, что get_by_email возвращает пользователя при найденном email."""
    mock_user_repo.get_by_email.return_value = example_user
    result = await user_service.get_by_email(example_user.email)

    assert result == example_user
    mock_user_repo.get_by_email.assert_called_once_with(example_user.email)


@pytest.mark.asyncio
async def test_get_by_email_not_found(user_service: UserService, mock_user_repo: AsyncMock, example_user: User) -> None:
    """Проверяет, что get_by_email выбрасывает исключение при не найденном email."""
    mock_user_repo.get_by_email.return_value = None

    with pytest.raises(UserNotFoundException):
        await user_service.get_by_email(example_user.email)


@pytest.mark.asyncio
async def test_update_user_profile_success(
    user_service: UserService, mock_user_repo: AsyncMock, example_user: User, faker: Faker
) -> None:
    """Проверяет, что update_user_profile обновляет профиль пользователя успешно."""
    mock_user_repo.get_by_id.return_value = example_user
    mock_user_repo.save.return_value = example_user
    new_firstname = faker.first_name()

    result = await user_service.update_profile(example_user.id, firstname=new_firstname)

    assert result == example_user
    mock_user_repo.get_by_id.assert_called_once_with(example_user.id)
    mock_user_repo.save.assert_called_once_with(example_user)
    assert example_user.firstname == new_firstname


@pytest.mark.asyncio
async def test_update_user_profile_not_found(
    user_service: UserService, mock_user_repo: AsyncMock, example_user: User, faker: Faker
) -> None:
    """Проверяет, что update_user_profile выбрасывает исключение при не найденном пользователе."""
    mock_user_repo.get_by_id.return_value = None
    new_firstname = faker.first_name()

    with pytest.raises(UserNotFoundException):
        await user_service.update_profile(example_user.id, firstname=new_firstname)


@pytest.mark.asyncio
async def test_login_or_create_existing_user(
    user_service: UserService, mock_user_repo: AsyncMock, example_user: User, faker: Faker
) -> None:
    """Проверяет, что login_or_create синхронизирует email для существующего пользователя."""
    mock_user_repo.get_by_oauth.return_value = example_user
    mock_user_repo.save.return_value = example_user
    new_email = faker.email()
    new_firstname = faker.first_name()
    new_lastname = faker.last_name()

    result = await user_service.login_or_create(
        email=new_email,
        firstname=new_firstname,
        lastname=new_lastname,
        oauth_provider=example_user.oauth_provider,
        oauth_id=example_user.oauth_id,
    )

    assert result == example_user
    assert result.email == new_email
    mock_user_repo.get_by_oauth.assert_called_once_with(example_user.oauth_provider, example_user.oauth_id)
    mock_user_repo.save.assert_called_once_with(example_user)
    mock_user_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_login_or_create_new_user(
    user_service: UserService, mock_user_repo: AsyncMock, example_user: User, faker: Faker
) -> None:
    """Проверяет, что login_or_create создаёт нового пользователя при первом входе."""
    mock_user_repo.get_by_oauth.return_value = None
    mock_user_repo.create.side_effect = lambda user: user
    email = faker.email()
    firstname = faker.first_name()
    lastname = faker.last_name()
    oauth_provider = "google"
    oauth_id = faker.numerify("#" * 21)

    result = await user_service.login_or_create(
        email=email,
        firstname=firstname,
        lastname=lastname,
        oauth_provider=oauth_provider,
        oauth_id=oauth_id,
    )

    assert result.email == email
    assert result.firstname == firstname
    assert result.lastname == lastname
    assert result.oauth_provider == oauth_provider
    assert result.oauth_id == oauth_id
    mock_user_repo.get_by_oauth.assert_called_once_with(oauth_provider, oauth_id)
    mock_user_repo.create.assert_called_once()
    mock_user_repo.save.assert_not_called()
