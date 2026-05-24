from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.user import User


class IUserRepository(ABC):
    """
    Интерфейс репозитория для работы с пользователями.
    """

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """
        Получить пользователя по ID.

        Args:
            user_id: Уникальный идентификатор пользователя

        Returns:
            Объект User или None, если пользователь не найден
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """
        Получить пользователя по email.

        Args:
            email: Email адрес

        Returns:
            Объект User или None, если пользователь не найден
        """
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Создать нового пользователя.

        Args:
            User: Объект User с данными пользователя

        Returns:
            Созданный объект User
        """
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        """
        Сохранить изменения пользователя.

        Args:
            User: Объект User с обновлёнными данными

        Returns:
            Сохранённый объект User
        """
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        """
        Удалить пользователя по ID

        Args:
            user_id: Уникальный идентификатор пользователя
        """
        pass
