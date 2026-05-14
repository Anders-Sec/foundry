import asyncio
from collections.abc import AsyncGenerator
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.auth.passwords import hash_password
from app.database import Base, get_session
from app.models import User


# ── Event loop ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def event_loop():  # type: ignore[no-untyped-def]
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Database container (session-scoped — one Postgres per test run) ───────────

@pytest.fixture(scope="session")
def pg_container():  # type: ignore[no-untyped-def]
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg


@pytest_asyncio.fixture(scope="session")
async def db_engine(pg_container: Any):  # type: ignore[no-untyped-def]
    url = pg_container.get_connection_url().replace("psycopg2", "asyncpg")
    engine = create_async_engine(url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine: Any) -> AsyncGenerator[AsyncSession, None]:
    """Each test gets its own transaction, rolled back at the end."""
    async with db_engine.connect() as conn:
        await conn.begin()
        session_factory = async_sessionmaker(
            bind=conn, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as session:
            yield session
        await conn.rollback()


# ── App and client fixtures ───────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    import os
    os.environ.setdefault("FOUNDRY_DATABASE_URL", "postgresql+asyncpg://x:x@localhost/x")
    os.environ.setdefault("FOUNDRY_JWT_SECRET", "test-secret-that-is-long-enough-for-tests")
    os.environ.setdefault("FOUNDRY_ENV", "development")
    os.environ.setdefault("FOUNDRY_COOKIE_SECURE", "false")

    from app.config import get_settings
    get_settings.cache_clear()  # type: ignore[attr-defined]

    from app.main import create_app
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session  # type: ignore[attr-defined]

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ── User fixtures ─────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def seed_admin(db_session: AsyncSession) -> User:
    user = User(
        id=uuid4(),
        username="admin",
        email="admin@foundry.local",
        password_hash=hash_password("test-password"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def authed_client(
    client: AsyncClient, seed_admin: User
) -> AsyncGenerator[AsyncClient, None]:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "test-password"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    yield client
