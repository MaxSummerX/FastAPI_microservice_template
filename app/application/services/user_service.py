from uuid import UUID

from app.application.exception import UserNotFoundException
from app.domain.entities.user import User
from app.domain.repositories.users import IUserRepository


class UserService:
    def __init__(self, user_repo: IUserRepository) -> None:
        self.user_repo = user_repo

    async def get_by_id(self, user_id: UUID) -> User:
        """
        Получает пользователя по ID.

        Args:
            user_id: Уникальный идентификатор пользователя

        Returns:
            Объект User
        Raises:
            UserNotFoundException: Если пользователь не найден
        """
        result = await self.user_repo.get_by_id(user_id)
        if not result:
            raise UserNotFoundException()
        return result

    async def get_by_email(self, email: str) -> User:
        """
        Получает пользователя по email.

        Args:
            email: Email пользователя

        Returns:
            Объект User
        Raises:
            UserNotFoundException: Если пользователь не найден
        """
        result = await self.user_repo.get_by_email(email)
        if not result:
            raise UserNotFoundException()
        return result

    async def update_profile(self, user_id: UUID, firstname: str | None = None, lastname: str | None = None) -> User:
        """
        Обновляет профиль пользователя.

        Args:
            user_id: Уникальный идентификатор пользователя
            firstname: Новое имя пользователя
            lastname: Новая фамилия пользователя

        Returns:
            Объект User
        Raises:
            UserNotFoundException: Если пользователь не найден
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        user.update_profile(firstname, lastname)
        return await self.user_repo.save(user)

    async def login_or_create(
        self, email: str, firstname: str, lastname: str, oauth_provider: str, oauth_id: str
    ) -> User:
        """
        Авторизует пользователя через OAuth. Создаёт нового при первом входе.

        Args:
            email: Email пользователя
            firstname: Имя пользователя
            lastname: Фамилия пользователя
            oauth_provider: Провайдер OAuth
            oauth_id: Уникальный идентификатор пользователя в OAuth

        Returns:
            Объект User
        """
        user = await self.user_repo.get_by_oauth(oauth_provider, oauth_id)
        if user:
            user.sync_from_oauth(email=email)
            return await self.user_repo.save(user)

        user = User.create_from_oauth(
            email=email, firstname=firstname, lastname=lastname, oauth_provider=oauth_provider, oauth_id=oauth_id
        )
        return await self.user_repo.create(user)
