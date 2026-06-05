from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.config import Settings
from app.domain.entities.user import User
from app.infrastructure.auth.jwt import create_access_token, decode_token


def test_create_access_token(example_user: User, test_settings: Settings) -> None:
    """Проверяет, что create_access_token создаёт валидный JWT-токен с правильными полями."""
    token = create_access_token(example_user.id, example_user.email)
    assert isinstance(token, str)
    payload = jwt.decode(
        token,
        key=test_settings.SECRET_KEY.get_secret_value(),
        algorithms=[test_settings.ALGORITHM],
        options={"verify_exp": False},
    )
    assert payload["sub"] == str(example_user.id)
    assert payload["email"] == example_user.email
    assert "exp" in payload


def test_decode_valid_token(example_user: User) -> None:
    """Проверяет, что decode_token декодирует валидный токен и возвращает payload."""
    token = create_access_token(example_user.id, example_user.email)
    payload = decode_token(token)
    assert payload["sub"] == str(example_user.id)
    assert payload["email"] == example_user.email


def test_decode_expired_token(example_user: User, test_settings: Settings) -> None:
    """Проверяет, что decode_token бросает ExpiredSignatureError для просроченного токена."""
    payload = {
        "sub": str(example_user.id),
        "email": example_user.email,
        "exp": datetime.now(UTC) - timedelta(minutes=10),
    }
    token = jwt.encode(
        payload=payload,
        key=test_settings.SECRET_KEY.get_secret_value(),
        algorithm=test_settings.ALGORITHM,
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(token)


def test_decode_invalid_token() -> None:
    """Проверяет, что decode_token бросает исключение для невалидного токена."""
    invalid_token = "invalid_token"
    with pytest.raises((jwt.DecodeError, jwt.InvalidTokenError)):
        decode_token(invalid_token)
