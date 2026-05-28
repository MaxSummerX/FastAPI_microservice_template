from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    id: UUID
    firstname: str | None
    lastname: str | None
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
