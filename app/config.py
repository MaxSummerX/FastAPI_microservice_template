from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


_PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    DATABASE_URL: str = Field(..., description="Строка подключения к БД(postgresql/mysql/sqlite)")

    SECRET_KEY: SecretStr = Field(..., description="Секретный ключ для JWT токенов")
    ALGORITHM: str = Field(default="HS256", description="Алгоритм шифрования JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Время жизни access токена в минутах")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Время жизни refresh токена в днях")

    DEBUG: bool = Field(default=False, description="Режим отладки")

    GOOGLE_CLIENT_ID: str = Field(..., description="Client ID для Google OAuth")
    GOOGLE_CLIENT_SECRET: SecretStr = Field(..., description="Client Secret для Google OAuth")
    GOOGLE_REDIRECT_URI: str = Field(..., description="URI обратного вызова после авторизации Google")


settings = Settings()
