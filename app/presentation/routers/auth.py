import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from app.application.services.user_service import UserService
from app.infrastructure.auth.jwt import create_access_token
from app.infrastructure.auth.providers.google import GoogleProvider
from app.infrastructure.auth.providers.provider_factory import get_google_provider
from app.presentation.dependencies import get_user_service
from app.presentation.schemas.auth import TokenResponse


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/google")
async def google_login(provider: GoogleProvider = Depends(get_google_provider)) -> RedirectResponse:
    """Перенаправляет пользователя на страницу авторизации Google."""
    url = await provider.get_login_url()
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@router.get("/google/callback")
async def google_callback(
    code: str, service: UserService = Depends(get_user_service), provider: GoogleProvider = Depends(get_google_provider)
) -> TokenResponse:
    """Обрабатывает callback от Google и аутентифицирует пользователя."""
    try:
        user_data = await provider.get_user_info(code)
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to authenticate with Google"
        ) from None
    user = await service.login_or_create(
        email=user_data.email,
        firstname=user_data.firstname,
        lastname=user_data.lastname,
        oauth_provider=user_data.oauth_provider,
        oauth_id=user_data.oauth_id,
    )
    access_token = create_access_token(user.id, user.email)
    return TokenResponse(access_token=access_token)
