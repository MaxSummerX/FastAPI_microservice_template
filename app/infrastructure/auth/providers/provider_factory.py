from app.config import settings
from app.infrastructure.auth.providers.google import GoogleProvider


def get_google_provider() -> GoogleProvider:
    """Возвращает экземпляр GoogleProvider."""
    return GoogleProvider(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET.get_secret_value(),
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )
