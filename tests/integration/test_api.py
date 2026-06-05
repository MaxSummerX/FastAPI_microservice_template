from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.domain.entities.user import User


@pytest.mark.asyncio
async def test_healthcheck(test_client: AsyncClient) -> None:
    response = await test_client.get("/health_check")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_readinesscheck(test_client: AsyncClient) -> None:
    response = await test_client.get("/readiness_check")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


@pytest.mark.asyncio
async def test_get_user_unauthorized(test_client: AsyncClient) -> None:
    response = await test_client.get(f"/api/v1/users/{uuid4()}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_user_forbidden(
    test_client: AsyncClient, db_user: User, other_user_auth_headers: dict[str, str]
) -> None:
    response = await test_client.get(f"/api/v1/users/{db_user.id}", headers=other_user_auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_user_success(test_client: AsyncClient, db_user: User, auth_headers: dict[str, str]) -> None:
    response = await test_client.get(f"/api/v1/users/{db_user.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "id": str(db_user.id),
        "email": db_user.email,
        "firstname": db_user.firstname,
        "lastname": db_user.lastname,
    }


@pytest.mark.asyncio
async def test_update_profile_success(test_client: AsyncClient, db_user: User, auth_headers: dict[str, str]) -> None:
    response = await test_client.patch(
        f"/api/v1/users/{db_user.id}",
        headers=auth_headers,
        json={"firstname": "new_firstname"},
    )
    assert response.status_code == 200
    assert response.json()["firstname"] == "new_firstname"


@pytest.mark.asyncio
async def test_update_profile_forbidden(
    test_client: AsyncClient, db_user: User, other_user_auth_headers: dict[str, str]
) -> None:
    response = await test_client.patch(
        f"/api/v1/users/{db_user.id}",
        headers=other_user_auth_headers,
        json={"firstname": "petuh"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_user_invalid_id(test_client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await test_client.get("/api/v1/users/not-a-uuid", headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_profile_invalid_data(
    test_client: AsyncClient, db_user: User, auth_headers: dict[str, str]
) -> None:
    response = await test_client.patch(
        f"/api/v1/users/{db_user.id}",
        headers=auth_headers,
        json={"firstname": ""},
    )
    assert response.status_code == 422
