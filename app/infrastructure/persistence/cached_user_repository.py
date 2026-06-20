import logging
from dataclasses import asdict
from uuid import UUID

import orjson

from app.domain.entities.user import User
from app.domain.repositories.users import IUserRepository
from app.infrastructure.cache.protocol.cache import ICache


logger = logging.getLogger(__name__)


class CachedUserRepository(IUserRepository):
    """
    Декоратор над IUserRepository.

    Cache-aside: чтение идёт через кэш (промах - запрос в БД с заполнением кэша),
    запись (save/delete) инвалидирует все ключи пользователя. Прозрачен для сервиса.
    """

    def __init__(self, repo: IUserRepository, cache: ICache, ttl: int = 3600) -> None:
        """
        Инициализирует декоратор.

        Args:
            repo: Оборачиваемый репозиторий
            cache: Абстракция кэша
            ttl: Время жизни записей в секундах (по умолчанию 3600)
        """
        self.repo = repo
        self.cache = cache
        self.ttl = ttl

    async def get_by_id(self, user_id: UUID) -> User | None:
        """
        Получает пользователя по ID. Кэширует результат.
        Используется логирование для демонстрации работы кэша.

        Args:
            user_id: Уникальный идентификатор пользователя

        Returns:
            Объект User или None, если пользователь не найден
        """
        key = f"user:{user_id}"
        cached = await self.cache.get(key)

        if cached is not None:
            logger.info("Чтение из кэша для user:%s", user_id)
            return self._deserialize(cached)

        logger.info("Чтение из бд для user:%s", user_id)
        result = await self.repo.get_by_id(user_id)

        if result is not None:
            logger.info("Запись в кэш для user:%s", user_id)
            await self.cache.set(key, self._serialize(result), ttl=self.ttl)  # Сразу пустить в фон через create_task?

        return result

    async def get_by_email(self, email: str) -> User | None:
        """
        Получает пользователя по email. Кэширует результат.

        Args:
            email: Email пользователя

        Returns:
            Объект User или None, если пользователь не найден
        """
        key = f"user:email:{email}"
        cached = await self.cache.get(key)

        if cached is not None:
            return self._deserialize(cached)

        result = await self.repo.get_by_email(email)

        if result is not None:
            await self.cache.set(key, self._serialize(result), ttl=self.ttl)  # Сразу пустить в фон через create_task?

        return result

    async def create(self, user: User) -> User:
        """
        Создать нового пользователя (делегирует оборачиваемому репозиторию).

        Args:
            user: Объект User с данными пользователя

        Returns:
            Созданный объект User
        """
        return await self.repo.create(user)

    async def save(self, user: User) -> User:
        """
        Сохранить изменения и инвалидировать кэш пользователя.

        Args:
            user: Объект User с обновлёнными данными

        Returns:
            Сохранённый объект User
        """

        saved = await self.repo.save(user)

        await self.cache.delete(f"user:{user.id}")
        await self.cache.delete(f"user:email:{user.email}")
        await self.cache.delete(f"user:oauth:{user.oauth_provider}:{user.oauth_id}")

        return saved

    async def delete(self, user_id: UUID) -> None:
        """
        Удалить пользователя по ID и инвалидировать кэш.

        Args:
            user_id: Уникальный идентификатор пользователя
        """
        user = await self.repo.get_by_id(user_id)

        if user is not None:
            await self.repo.delete(user_id)
            await self.cache.delete(f"user:{user.id}")
            await self.cache.delete(f"user:email:{user.email}")
            await self.cache.delete(f"user:oauth:{user.oauth_provider}:{user.oauth_id}")

    async def get_by_oauth(self, oauth_provider: str, oauth_id: str) -> User | None:
        """
        Найти пользователя по OAuth провайдеру и ID. Кэширует результат.

        Args:
            oauth_provider: Название OAuth провайдера
            oauth_id: Уникальный идентификатор пользователя в OAuth

        Returns:
            Объект User или None, если пользователь не найден
        """
        key = f"user:oauth:{oauth_provider}:{oauth_id}"
        cached = await self.cache.get(key)

        if cached is not None:
            return self._deserialize(cached)

        result = await self.repo.get_by_oauth(oauth_provider, oauth_id)

        if result is not None:
            await self.cache.set(key, self._serialize(result), ttl=self.ttl)

        return result

    def _deserialize(self, raw: str) -> User:
        """Десериализует строку в объект User."""
        data = orjson.loads(raw)
        data["id"] = UUID(data["id"])
        return User(**data)

    def _serialize(self, user: User) -> str:
        """Сериализует объект User в строку."""
        data = asdict(user)
        data.pop("_events", None)
        data["id"] = str(data["id"])
        return orjson.dumps(data).decode()
