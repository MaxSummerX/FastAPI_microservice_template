from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.exception import UserNotFoundException
from app.application.services.user_service import UserService
from app.domain.entities.user import User
from app.presentation.dependencies import get_current_user, get_user_service
from app.presentation.schemas.user import UserProfileUpdate, UserResponse


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Получает информацию о пользователе по его ID."""
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        user: User = await service.get_by_id(user_id)
        return UserResponse.model_validate(user)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") from None


@router.patch("/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(
    user_id: UUID,
    user_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Обновляет информацию о пользователе по его ID."""
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        user: User = await service.update_profile(
            user_id=user_id, firstname=user_data.firstname, lastname=user_data.lastname
        )
        return UserResponse.model_validate(user)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") from None
