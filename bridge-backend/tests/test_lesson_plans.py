"""Tests for lesson plan endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from tests.conftest import register_and_get_headers

pytestmark = pytest.mark.asyncio

MOCK_CLAUDE_RESPONSE = {
    "content": [
        {
            "type": "text",
            "text": '{"lesson_content": "# Test Lesson\\n\\nThis is a test lesson.", "practice_exercises": "## Exercise 1\\n\\nDo this.", "homework": "## Homework\\n\\nComplete this.", "language": "en"}',
        }
    ]
}


async def _setup_chat_with_messages(client: AsyncClient) -> tuple[str, dict, dict]:
    """Create client+specialist, chat room with messages, return (room_id, client_headers, spec_headers)."""
    _, client_headers = await register_and_get_headers(
        client, role="client", full_name="LP Client"
    )
    _, spec_headers = await register_and_get_headers(
        client, role="specialist", full_name="LP Specialist"
    )

    # Create specialist profile
    await client.post(
        "/specialists/profile",
        json={
            "headline": "Lesson Plan Expert",
            "bio": "Testing lesson plan generation.",
            "hourly_rate": 100.0,
            "domains": ["Education"],
            "languages": [{"language": "English", "proficiency": "native"}],
        },
        headers=spec_headers,
    )

    # Get specialist user ID
    me_resp = await client.get("/users/me", headers=spec_headers)
    spec_user = me_resp.json()

    # Create room
    room_resp = await client.post(
        "/chats/",
        json={"specialist_id": spec_user["id"]},
        headers=client_headers,
    )
    room_id = room_resp.json()["id"]

    # Send enough messages (minimum 2)
    await client.post(
        f"/chats/{room_id}/messages",
        json={"content": "I need help learning English B1 level."},
        headers=client_headers,
    )
    await client.post(
        f"/chats/{room_id}/messages",
        json={"content": "Sure! Let's start with conversational practice focused on travel topics."},
        headers=spec_headers,
    )
    await client.post(
        f"/chats/{room_id}/messages",
        json={"content": "That sounds great! I travel a lot for work."},
        headers=client_headers,
    )

    return room_id, client_headers, spec_headers


async def test_generate_lesson_plan(client: AsyncClient) -> None:
    """Test lesson plan generation with mocked Claude API."""
    room_id, client_headers, spec_headers = await _setup_chat_with_messages(client)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_CLAUDE_RESPONSE

    with patch("app.services.lesson_plan_service.httpx.AsyncClient") as mock_client_class, \
         patch("app.services.lesson_plan_service.settings") as mock_settings:
        mock_settings.ANTHROPIC_API_KEY = "test-fake-key"
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client_instance

        resp = await client.post(
            "/lesson-plans/generate",
            json={"room_id": room_id},
            headers=spec_headers,
        )

    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "completed"
    assert "Test Lesson" in data["lesson_content"]
    assert data["language"] == "en"


async def test_generate_lesson_plan_as_client_forbidden(client: AsyncClient) -> None:
    """Only specialists can generate lesson plans."""
    room_id, client_headers, spec_headers = await _setup_chat_with_messages(client)

    resp = await client.post(
        "/lesson-plans/generate",
        json={"room_id": room_id},
        headers=client_headers,
    )
    assert resp.status_code == 403


async def test_get_room_lesson_plans(client: AsyncClient) -> None:
    """Both client and specialist can view lesson plans."""
    room_id, client_headers, spec_headers = await _setup_chat_with_messages(client)

    # Generate a plan first (mocked)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_CLAUDE_RESPONSE

    with patch("app.services.lesson_plan_service.httpx.AsyncClient") as mock_client_class, \
         patch("app.services.lesson_plan_service.settings") as mock_settings:
        mock_settings.ANTHROPIC_API_KEY = "test-fake-key"
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client_instance

        await client.post(
            "/lesson-plans/generate",
            json={"room_id": room_id},
            headers=spec_headers,
        )

    # Both can view
    for headers in [spec_headers, client_headers]:
        resp = await client.get(f"/lesson-plans/room/{room_id}", headers=headers)
        assert resp.status_code == 200
        plans = resp.json()
        assert len(plans) >= 1


async def test_generate_lesson_plan_not_enough_messages(client: AsyncClient) -> None:
    """Should fail if chat has fewer than 2 messages."""
    _, client_headers = await register_and_get_headers(
        client, role="client", full_name="Empty Chat Client"
    )
    _, spec_headers = await register_and_get_headers(
        client, role="specialist", full_name="Empty Chat Specialist"
    )

    await client.post(
        "/specialists/profile",
        json={
            "headline": "Empty Chat Expert",
            "bio": "Test.",
            "hourly_rate": 50.0,
            "domains": ["Other"],
            "languages": [{"language": "English", "proficiency": "native"}],
        },
        headers=spec_headers,
    )

    me_resp = await client.get("/users/me", headers=spec_headers)
    spec_user = me_resp.json()

    room_resp = await client.post(
        "/chats/",
        json={"specialist_id": spec_user["id"]},
        headers=client_headers,
    )
    room_id = room_resp.json()["id"]

    # Only 1 message
    await client.post(
        f"/chats/{room_id}/messages",
        json={"content": "Hello"},
        headers=client_headers,
    )

    resp = await client.post(
        "/lesson-plans/generate",
        json={"room_id": room_id},
        headers=spec_headers,
    )
    assert resp.status_code == 400
