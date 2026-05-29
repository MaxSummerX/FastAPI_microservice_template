from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.user_service import UserService
from app.domain.entities.user import User
from app.domain.repositories.users import IUserRepository
from app.infrastructure.auth.jwt import decode_token
from app.infrastructure.database.dependencies import get_db
from app.infrastructure.persistence.sqlalchemy.user_repository import UserSQLAlchemyRepository


bearer_scheme = HTTPBearer()


def get_user_repo(db: AsyncSession = Depends(get_db)) -> IUserRepository:
    """Возвращает репозиторий пользователей."""
    return UserSQLAlchemyRepository(db)


def get_user_service(repo: IUserRepository = Depends(get_user_repo)) -> UserService:
    """Возвращает сервис пользователей."""
    return UserService(repo)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_repo: IUserRepository = Depends(get_user_repo),
) -> User:
    """
    Аутентифицирует пользователя и возвращает его.

    Args:
        credentials: Данные авторизации из заголовка
        user_repo: Репозиторий пользователей

    Returns:
        Аутентифицированный пользователь

    Raises:
        HTTPException 401: Токен отсутствует, просрочен, невалиден или пользователь не найден
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception from None

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired", headers={"WWW-Authenticate": "Bearer"}
        ) from None
    except (jwt.DecodeError, jwt.InvalidTokenError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from None

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception from None

    user = await user_repo.get_by_id(user_uuid)
    if user is None:
        raise credentials_exception from None
    return user
