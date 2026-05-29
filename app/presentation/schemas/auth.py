from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str = Field(description="JWT access токен для API запросов")
    token_type: str = Field(default="bearer", description="Тип токена")
