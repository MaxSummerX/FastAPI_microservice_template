from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from app.config import settings


def create_access_token(user_id: UUID, user_email: str) -> str:
    """Создает access токен для пользователя."""
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "email": user_email, "exp": expire}
    return jwt.encode(payload=payload, key=settings.SECRET_KEY.get_secret_value(), algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """Декодирует токен и возвращает его содержимое."""
    return jwt.decode(jwt=token, key=settings.SECRET_KEY.get_secret_value(), algorithms=settings.ALGORITHM)
