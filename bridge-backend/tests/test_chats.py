"""Tests for chat endpoints."""

import pytest
from httpx import AsyncClient

from tests.conftest import register_and_get_headers

pytestmark = pytest.mark.asyncio


async def _setup_chat_users(client: AsyncClient) -> tuple[dict, dict, dict, dict]:
    """Create a client and specialist, return their data and headers."""
    client_data, client_headers = await register_and_get_headers(
        client, role="client", full_name="Chat Client"
    )
    spec_data, spec_headers = await register_and_get_headers(
        client, role="specialist", full_name="Chat Specialist"
    )

    # Create specialist profile
    await client.post(
        "/specialists/profile",
        json={
            "headline": "Chat Test Expert",
            "bio": "Testing chat functionality.",
            "hourly_rate": 50.0,
            "domains": ["Education"],
            "languages": [{"language": "English", "proficiency": "native"}],
        },
        headers=spec_headers,
    )

    # Get specialist user ID
    me_resp = await client.get("/users/me", headers=spec_headers)
    spec_user = me_resp.json()

    return client_headers, spec_headers, client_data, spec_user


async def test_create_chat_room(client: AsyncClient) -> None:
    client_headers, spec_headers, _, spec_user = await _setup_chat_users(client)

    resp = await client.post(
        "/chats/",
        json={"specialist_id": spec_user["id"]},
        headers=client_headers,
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert "id" in data


async def test_get_my_chats(client: AsyncClient) -> None:
    client_headers, spec_headers, _, spec_user = await _setup_chat_users(client)

    # Create a room
    await client.post(
        "/chats/",
        json={"specialist_id": spec_user["id"]},
        headers=client_headers,
    )

    # Get chats
    resp = await client.get("/chats/", headers=client_headers)
    assert resp.status_code == 200
    chats = resp.json()
    assert len(chats) >= 1


async def test_send_and_get_messages(client: AsyncClient) -> None:
    client_headers, spec_headers, _, spec_user = await _setup_chat_users(client)

    # Create room
    room_resp = await client.post(
        "/chats/",
        json={"specialist_id": spec_user["id"]},
        headers=client_headers,
    )
    room_id = room_resp.json()["id"]

    # Send a message via REST
    msg_resp = await client.post(
        f"/chats/{room_id}/messages",
        json={"content": "Hello, this is a test message!"},
        headers=client_headers,
    )
    assert msg_resp.status_code == 201
    msg = msg_resp.json()
    assert msg["content"] == "Hello, this is a test message!"

    # Get messages
    msgs_resp = await client.get(f"/chats/{room_id}/messages", headers=client_headers)
    assert msgs_resp.status_code == 200
    messages = msgs_resp.json()
    assert len(messages) >= 1
    assert messages[0]["content"] == "Hello, this is a test message!"


async def test_unauthorized_chat_access(client: AsyncClient) -> None:
    """A user who is not a participant should get 403."""
    client_headers, spec_headers, _, spec_user = await _setup_chat_users(client)

    # Create room between client and specialist
    room_resp = await client.post(
        "/chats/",
        json={"specialist_id": spec_user["id"]},
        headers=client_headers,
    )
    room_id = room_resp.json()["id"]

    # Third user tries to access
    _, outsider_headers = await register_and_get_headers(
        client, role="client", full_name="Outsider"
    )
    resp = await client.get(f"/chats/{room_id}/messages", headers=outsider_headers)
    assert resp.status_code == 403


async def test_mark_chat_read(client: AsyncClient) -> None:
    client_headers, spec_headers, _, spec_user = await _setup_chat_users(client)

    # Create room and send message
    room_resp = await client.post(
        "/chats/",
        json={"specialist_id": spec_user["id"]},
        headers=client_headers,
    )
    room_id = room_resp.json()["id"]

    await client.post(
        f"/chats/{room_id}/messages",
        json={"content": "Test unread message"},
        headers=client_headers,
    )

    # Specialist marks as read
    resp = await client.patch(f"/chats/{room_id}/read", headers=spec_headers)
    assert resp.status_code in (200, 204)
