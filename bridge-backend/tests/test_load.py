"""Basic load tests for Bridge API.

Tests concurrent REST requests to verify the app handles multiple simultaneous users.
"""

import asyncio
import time

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

pytestmark = pytest.mark.asyncio

CONCURRENT_USERS = 10
BASE_URL = "http://test"


async def _make_request(client: AsyncClient, path: str) -> tuple[int, float]:
    """Make a single request, return (status_code, latency_ms)."""
    start = time.monotonic()
    resp = await client.get(path)
    latency = (time.monotonic() - start) * 1000
    return resp.status_code, latency


async def test_concurrent_specialist_search() -> None:
    """10 concurrent users searching for specialists."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]

    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        # First register a user to get auth headers
        resp = await client.post(
            "/auth/register",
            json={
                "email": "loadtest@demo.com",
                "password": "TestPass123!",
                "full_name": "Load Test User",
                "role": "client",
            },
        )
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Run concurrent requests
        tasks = [
            _make_request(
                AsyncClient(
                    transport=transport,
                    base_url=BASE_URL,
                    headers=headers,
                ),
                "/specialists/",
            )
            for _ in range(CONCURRENT_USERS)
        ]

        results = await asyncio.gather(*tasks)

    statuses = [r[0] for r in results]
    latencies = [r[1] for r in results]

    # All requests should succeed
    assert all(s == 200 for s in statuses), f"Some requests failed: {statuses}"

    # Performance check
    avg_latency = sum(latencies) / len(latencies)
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

    print(f"\n  Concurrent specialist search ({CONCURRENT_USERS} users):")
    print(f"  Avg latency: {avg_latency:.1f}ms")
    print(f"  P95 latency: {p95_latency:.1f}ms")
    print(f"  Max latency: {max(latencies):.1f}ms")

    # Reasonable threshold for local testing
    assert p95_latency < 2000, f"P95 latency too high: {p95_latency:.1f}ms"


async def test_concurrent_auth_requests() -> None:
    """10 concurrent user registrations."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]

    async def register_one(i: int) -> tuple[int, float]:
        async with AsyncClient(transport=transport, base_url=BASE_URL) as c:
            start = time.monotonic()
            resp = await c.post(
                "/auth/register",
                json={
                    "email": f"loadtest_reg_{i}@demo.com",
                    "password": "TestPass123!",
                    "full_name": f"Load User {i}",
                    "role": "client",
                },
            )
            latency = (time.monotonic() - start) * 1000
            return resp.status_code, latency

    results = await asyncio.gather(*[register_one(i) for i in range(CONCURRENT_USERS)])

    statuses = [r[0] for r in results]
    latencies = [r[1] for r in results]

    success_count = sum(1 for s in statuses if s == 201)
    print(f"\n  Concurrent registrations ({CONCURRENT_USERS} users):")
    print(f"  Successful: {success_count}/{CONCURRENT_USERS}")
    print(f"  Avg latency: {sum(latencies)/len(latencies):.1f}ms")

    assert success_count == CONCURRENT_USERS
