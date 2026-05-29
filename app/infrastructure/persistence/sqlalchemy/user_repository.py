from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.repositories.users import IUserRepository
from app.infrastructure.persistence.models import User as UserModel


class UserSQLAlchemyRepository(IUserRepository):
    """
    SQLAlchemy реализация репозитория пользователей.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Инициализирует репозиторий.

        Args:
            db: Асинхронная сессия SQLAlchemy
        """
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        """
        Получить пользователя по ID.

        Args:
            user_id: Уникальный идентификатор пользователя

        Returns:
            Объект User или None, если пользователь не найден
        """
        db_user = await self.db.scalar(select(UserModel).where(UserModel.id == user_id))

        if db_user:
            return self._to_domain(db_user)
        return None

    async def get_by_email(self, email: str) -> User | None:
        """
        Получить пользователя по email.

        Args:
            email: Email адрес

        Returns:
            Объект User или None, если пользователь не найден
        """
        db_user = await self.db.scalar(select(UserModel).where(UserModel.email == email))
        if db_user:
            return self._to_domain(db_user)
        return None

    async def create(self, user: User) -> User:
        """
        Создать нового пользователя.

        Args:
            User: Объект User с данными пользователя

        Returns:
            Созданный объект User
        """
        db_user = self._to_model(user)
        self.db.add(db_user)
        await self.db.commit()
        return user

    async def save(self, user: User) -> User:
        """
        Сохранить изменения пользователя.

        Args:
            User: Объект User с обновлёнными данными

        Returns:
            Сохранённый объект User
        """
        db_user = self._to_model(user)
        await self.db.merge(db_user)  # Скрытый INSERT
        await self.db.commit()
        return user

    async def delete(self, user_id: UUID) -> None:
        """
        Удалить пользователя по ID

        Args:
            user_id: Уникальный идентификатор пользователя
        """
        raise NotImplementedError  # TODO: Реализовать позже, нужно мягкое удаление

    async def get_by_oauth(self, oauth_provider: str, oauth_id: str) -> User | None:
        """
        Найти пользователя по OAuth провайдеру и ID.

        Args:
            oauth_provider: Название OAuth провайдера
            oauth_id: Уникальный идентификатор пользователя в OAuth

        Returns:
            Объект User или None, если пользователь не найден
        """
        db_user = await self.db.scalar(
            select(UserModel).where(UserModel.oauth_provider == oauth_provider, UserModel.oauth_id == oauth_id)
        )
        if db_user:
            return self._to_domain(db_user)

        return None

    def _to_domain(self, db_user: UserModel) -> User:
        """Преобразует ORM-модель в доменную сущность User."""
        return User(
            id=db_user.id,
            firstname=db_user.firstname,
            lastname=db_user.lastname,
            email=db_user.email,
            oauth_provider=db_user.oauth_provider,
            oauth_id=db_user.oauth_id,
        )

    def _to_model(self, user: User) -> UserModel:
        """Преобразует доменную сущность User в ORM-модель."""
        return UserModel(
            id=user.id,
            firstname=user.firstname,
            lastname=user.lastname,
            email=user.email,
            oauth_provider=user.oauth_provider,
            oauth_id=user.oauth_id,
        )
