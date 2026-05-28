from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.user_service import UserService
from app.domain.repositories.users import IUserRepository
from app.infrastructure.database.dependencies import get_db
from app.infrastructure.persistence.sqlalchemy.user_repository import UserSQLAlchemyRepository


def get_user_repo(db: AsyncSession = Depends(get_db)) -> IUserRepository:
    return UserSQLAlchemyRepository(db)


def get_user_service(repo: IUserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(repo)
