from uuid import UUID

from app.application.exception import UserNotFoundException
from app.domain.entities.user import User
from app.domain.repositories.users import IUserRepository


class UserService:
    def __init__(self, user_repo: IUserRepository) -> None:
        self.user_repo = user_repo

    async def get_by_id(self, user_id: UUID) -> User:
        result = await self.user_repo.get_by_id(user_id)
        if not result:
            raise UserNotFoundException()
        return result

    async def get_by_email(self, email: str) -> User:
        result = await self.user_repo.get_by_email(email)
        if not result:
            raise UserNotFoundException()
        return result

    async def update_profile(self, user_id: UUID, firstname: str | None = None, lastname: str | None = None) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        user.update_profile(firstname, lastname)
        return await self.user_repo.save(user)
