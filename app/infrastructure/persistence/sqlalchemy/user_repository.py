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
            return User(id=db_user.id, firstname=db_user.firstname, lastname=db_user.lastname, email=db_user.email)
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
            return User(id=db_user.id, firstname=db_user.firstname, lastname=db_user.lastname, email=db_user.email)
        return None

    async def create(self, user: User) -> User:
        """
        Создать нового пользователя.

        Args:
            User: Объект User с данными пользователя

        Returns:
            Созданный объект User
        """
        db_user = UserModel(id=user.id, firstname=user.firstname, lastname=user.lastname, email=user.email)
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
        db_user = UserModel(id=user.id, firstname=user.firstname, lastname=user.lastname, email=user.email)
        await self.db.merge(db_user)
        await self.db.commit()
        return user

    async def delete(self, user_id: UUID) -> None:
        """
        Удалить пользователя по ID

        Args:
            user_id: Уникальный идентификатор пользователя
        """
        raise NotImplementedError  # TODO: Реализовать позже, нужно мягкое удаление
