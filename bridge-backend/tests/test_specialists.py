"""Tests for specialist endpoints."""

import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers, register_and_get_headers

pytestmark = pytest.mark.asyncio


async def test_search_specialists_unauthenticated(client: AsyncClient) -> None:
    """Public search should work without auth."""
    headers = await auth_headers(client, role="client")
    resp = await client.get("/specialists/", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_create_specialist_profile(client: AsyncClient) -> None:
    headers = await auth_headers(client, role="specialist")
    resp = await client.post(
        "/specialists/profile",
        json={
            "headline": "Test Expert",
            "bio": "I am a test expert with years of experience.",
            "hourly_rate": 100.0,
            "domains": ["AI/ML", "Science"],
            "languages": [{"language": "English", "proficiency": "native"}],
        },
        headers=headers,
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["headline"] == "Test Expert"


async def test_create_profile_as_client_forbidden(client: AsyncClient) -> None:
    headers = await auth_headers(client, role="client")
    resp = await client.post(
        "/specialists/profile",
        json={
            "headline": "Should Fail",
            "bio": "Clients cannot create specialist profiles.",
            "hourly_rate": 50.0,
            "domains": ["Law"],
            "languages": [{"language": "English", "proficiency": "native"}],
        },
        headers=headers,
    )
    assert resp.status_code == 403


async def test_update_availability(client: AsyncClient) -> None:
    headers = await auth_headers(client, role="specialist")
    # First create a profile
    await client.post(
        "/specialists/profile",
        json={
            "headline": "Availability Test",
            "bio": "Testing availability toggle.",
            "hourly_rate": 75.0,
            "domains": ["Education"],
            "languages": [{"language": "English", "proficiency": "fluent"}],
        },
        headers=headers,
    )
    # Toggle availability
    resp = await client.patch(
        "/specialists/availability",
        json={"availability": "busy"},
        headers=headers,
    )
    assert resp.status_code == 200
