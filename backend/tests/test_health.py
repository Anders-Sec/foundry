import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_liveness(client: AsyncClient) -> None:
    resp = await client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_readiness_up(client: AsyncClient) -> None:
    resp = await client.get("/readyz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_readiness_db_down(client: AsyncClient) -> None:
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.database import get_session

    async def broken_session():  # type: ignore[no-untyped-def]
        mock = AsyncMock(spec=AsyncSession)
        mock.execute.side_effect = Exception("DB unreachable")
        yield mock

    from app.main import create_app
    app = create_app()
    app.dependency_overrides[get_session] = broken_session  # type: ignore[attr-defined]

    from httpx import ASGITransport, AsyncClient as TestClient
    async with TestClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/readyz")
        assert resp.status_code == 503
