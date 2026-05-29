from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class OAuthUserInfo:
    email: str
    firstname: str
    lastname: str
    oauth_provider: str
    oauth_id: str


class OAuthProvider(ABC):
    @abstractmethod
    async def get_login_url(self) -> str:
        """Возвращает URL для перенаправления пользователя на страницу авторизации."""
        pass

    @abstractmethod
    async def get_user_info(self, code: str) -> OAuthUserInfo:
        """Возвращает информацию о пользователе после успешной авторизации."""
        pass
