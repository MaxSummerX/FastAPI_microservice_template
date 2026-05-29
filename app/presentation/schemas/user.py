from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserResponse(BaseModel):
    id: UUID = Field(description="Уникальный идентификатор пользователя")
    firstname: str | None = Field(default=None, description="Имя пользователя")
    lastname: str | None = Field(default=None, description="Фамилия пользователя")
    email: str = Field(description="Email пользователя")

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    firstname: str | None = Field(default=None, min_length=3, max_length=50, description="Имя пользователя")
    lastname: str | None = Field(default=None, min_length=3, max_length=50, description="Фамилия пользователя")

    model_config = ConfigDict(str_strip_whitespace=True)
