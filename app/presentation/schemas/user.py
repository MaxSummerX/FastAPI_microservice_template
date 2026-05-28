from uuid import UUID

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: UUID
    firstname: str | None
    lastname: str | None
    email: str


class UserProfileUpdate(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
