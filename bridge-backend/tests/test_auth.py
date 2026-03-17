"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers, register_user

pytestmark = pytest.mark.asyncio


async def test_register_client(client: AsyncClient) -> None:
    data = await register_user(client, role="client", full_name="Alice Test")
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_register_specialist(client: AsyncClient) -> None:
    data = await register_user(client, role="specialist", full_name="Dr. Test")
    assert "access_token" in data
    assert "refresh_token" in data


async def test_register_duplicate_email(client: AsyncClient) -> None:
    email = "duplicate@test.com"
    await register_user(client, email=email)
    resp = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "TestPass123!",
            "full_name": "Duplicate",
            "role": "client",
        },
    )
    assert resp.status_code in (400, 409)


async def test_login_success(client: AsyncClient) -> None:
    email = "login_test@demo.com"
    await register_user(client, email=email)
    resp = await client.post(
        "/auth/login",
        json={"email": email, "password": "TestPass123!"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


async def test_login_wrong_password(client: AsyncClient) -> None:
    email = "wrong_pass@demo.com"
    await register_user(client, email=email)
    resp = await client.post(
        "/auth/login",
        json={"email": email, "password": "WrongPassword!"},
    )
    assert resp.status_code == 401


async def test_login_nonexistent_email(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/login",
        json={"email": "nobody@demo.com", "password": "TestPass123!"},
    )
    assert resp.status_code == 401


async def test_refresh_token(client: AsyncClient) -> None:
    data = await register_user(client)
    resp = await client.post(
        "/auth/refresh",
        json={"refresh_token": data["refresh_token"]},
    )
    assert resp.status_code == 200
    new_data = resp.json()
    assert "access_token" in new_data
    # Token might be the same if generated within the same second (same exp claim)
    # Just verify we got a valid token back
    assert len(new_data["access_token"]) > 20


async def test_refresh_invalid_token(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/refresh",
        json={"refresh_token": "invalid-token-here"},
    )
    assert resp.status_code == 401


async def test_get_current_user(client: AsyncClient) -> None:
    headers = await auth_headers(client, role="client")
    resp = await client.get("/users/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "client"
    assert "email" in data
