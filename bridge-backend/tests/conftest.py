"""Test fixtures for Bridge API tests.

Replaces the app's database engine with a NullPool engine created on the test
event loop, avoiding asyncpg 'Future attached to a different loop' errors.
"""

import uuid
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import app.database as db_module
from app.config import settings
from app.models.user import Base

# Import all models so Base.metadata knows about them
from app.models.specialist import SpecialistProfile  # noqa: F401
from app.models.review import Review  # noqa: F401
from app.models.chat import ChatRoom, Message  # noqa: F401
from app.models.task_request import TaskRequest, TaskProposal  # noqa: F401
from app.models.lesson_plan import LessonPlan  # noqa: F401


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def _patch_db():
    """Replace app.database engine + session factory with test-loop versions.

    Uses NullPool to avoid connection-pool loop affinity issues.
    """
    # Create a fresh engine on the test event loop (NullPool = no pooling)
    test_engine = create_async_engine(
        settings.DATABASE_URL, echo=False, poolclass=NullPool
    )
    test_session_factory = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    # Monkey-patch the database module so the entire app uses the new engine
    original_engine = db_module.engine
    original_session = db_module.async_session
    original_get_db = db_module.get_db

    db_module.engine = test_engine
    db_module.async_session = test_session_factory

    # Also replace get_db to be safe (in case it was captured by reference)
    async def test_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with test_session_factory() as session:
            yield session

    db_module.get_db = test_get_db

    # Patch the FastAPI dependency too
    from app.main import app
    app.dependency_overrides[original_get_db] = test_get_db

    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield test_engine

    # Teardown
    app.dependency_overrides.clear()
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

    db_module.engine = original_engine
    db_module.async_session = original_session
    db_module.get_db = original_get_db


@pytest_asyncio.fixture(loop_scope="session")
async def client(_patch_db) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client using the patched database."""
    from app.main import app

    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ── Helper functions ──────────────────────────────────────────────────


async def register_user(
    client: AsyncClient,
    role: str = "client",
    email: str | None = None,
    full_name: str = "Test User",
) -> dict:
    """Register a user and return token response."""
    if email is None:
        email = f"test_{uuid.uuid4().hex[:8]}@demo.com"
    resp = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "TestPass123!",
            "full_name": full_name,
            "role": role,
        },
    )
    assert resp.status_code == 201, f"Registration failed: {resp.text}"
    return resp.json()


async def auth_headers(client: AsyncClient, role: str = "client") -> dict:
    """Register a user and return auth headers."""
    data = await register_user(client, role=role)
    return {"Authorization": f"Bearer {data['access_token']}"}


async def register_and_get_headers(
    client: AsyncClient,
    role: str,
    email: str | None = None,
    full_name: str = "Test User",
) -> tuple[dict, dict]:
    """Register user, return (token_data, auth_headers)."""
    data = await register_user(client, role=role, email=email, full_name=full_name)
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    return data, headers
