from uuid import UUID

from faker import Faker

from app.domain.entities.user import User


def test_create_user_from_oauth(faker: Faker) -> None:
    """Проверяет, корректное создание пользователя"""
    email = faker.email()
    firstname = faker.first_name()
    lastname = faker.last_name()
    oauth_provider = "google"
    oauth_id = faker.numerify("#" * 21)

    user = User.create_from_oauth(
        email=email,
        firstname=firstname,
        lastname=lastname,
        oauth_provider=oauth_provider,
        oauth_id=oauth_id,
    )

    assert isinstance(user.id, UUID)
    assert user.email == email
    assert user.firstname == firstname
    assert user.lastname == lastname
    assert user.oauth_provider == oauth_provider
    assert user.oauth_id == oauth_id


def test_sync_from_oauth(example_user: User, faker: Faker) -> None:
    """Проверяет, что синхронизация OAuth обновляет только email"""
    original_firstname = example_user.firstname
    original_lastname = example_user.lastname
    new_email = faker.email()

    example_user.sync_from_oauth(email=new_email)

    assert example_user.email == new_email
    assert example_user.firstname == original_firstname
    assert example_user.lastname == original_lastname


def test_update_profile_firstname(example_user: User, faker: Faker) -> None:
    """Проверяет, что update_profile обновляет только firstname"""
    original_lastname = example_user.lastname
    new_firstname = faker.first_name()
    example_user.update_profile(firstname=new_firstname)

    assert example_user.firstname == new_firstname
    assert example_user.lastname == original_lastname


def test_update_profile_lastname(example_user: User, faker: Faker) -> None:
    """Проверяет, что update_profile обновляет только lastname"""
    original_firstname = example_user.firstname
    new_lastname = faker.last_name()
    example_user.update_profile(lastname=new_lastname)

    assert example_user.firstname == original_firstname
    assert example_user.lastname == new_lastname


def test_update_profile_none(example_user: User) -> None:
    """Проверяет, что update_profile с None не изменяет ни одно поле пользователя."""
    original_firstname = example_user.firstname
    original_lastname = example_user.lastname

    example_user.update_profile(firstname=None, lastname=None)

    assert example_user.firstname == original_firstname
    assert example_user.lastname == original_lastname
