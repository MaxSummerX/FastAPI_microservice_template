import urllib.parse

import httpx

from app.infrastructure.auth.providers.base import OAuthProvider, OAuthUserInfo


class GoogleProvider(OAuthProvider):
    """Провайдер аутентификации через Google."""

    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"  # nosec B105
    USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    async def get_login_url(self) -> str:
        """Возвращает URL для перенаправления пользователя на страницу авторизации."""
        query_params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(["openid", "profile", "email"]),
        }
        query_string = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote)
        return f"{self.AUTH_URL}?{query_string}"

    async def get_user_info(self, code: str) -> OAuthUserInfo:
        """Возвращает информацию о пользователе после успешной авторизации."""
        async with httpx.AsyncClient() as client:
            token = await client.post(
                self.TOKEN_URL,
                data={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            token_data = token.json()
            user_response = await client.get(
                self.USERINFO_URL,
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            userinfo = user_response.json()

        return OAuthUserInfo(
            email=userinfo["email"],
            firstname=userinfo.get("given_name", ""),
            lastname=userinfo.get("family_name", ""),
            oauth_provider="google",
            oauth_id=userinfo["sub"],
        )
