import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.passwords import hash_password
from app.models import Detection, DetectionStatus, Severity, User


@pytest.fixture
async def seed_detections(db_session: AsyncSession, seed_admin: User) -> list[Detection]:
    detections = [
        Detection(
            name="Test Detection Alpha",
            description="First test detection",
            severity=Severity.high,
            status=DetectionStatus.active,
            query="event.type:alert",
            author_id=seed_admin.id,
        ),
        Detection(
            name="Test Detection Beta",
            description="Second test detection",
            severity=Severity.low,
            status=DetectionStatus.draft,
            query="event.type:info",
            author_id=seed_admin.id,
        ),
    ]
    for d in detections:
        db_session.add(d)
    await db_session.flush()
    return detections


@pytest.mark.asyncio
async def test_list_detections_returns_envelope(
    authed_client: AsyncClient, seed_detections: list[Detection]
) -> None:
    resp = await authed_client.get("/api/v1/detections")
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body
    assert body["total"] == len(seed_detections)
    assert len(body["items"]) == len(seed_detections)


@pytest.mark.asyncio
async def test_list_detections_item_shape(
    authed_client: AsyncClient, seed_detections: list[Detection]
) -> None:
    resp = await authed_client.get("/api/v1/detections")
    item = resp.json()["items"][0]
    for field in ("id", "name", "description", "severity", "status", "author_id",
                  "created_at", "updated_at"):
        assert field in item, f"Missing field: {field}"
    assert "query" not in item


@pytest.mark.asyncio
async def test_list_detections_unauthenticated(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/detections")
    assert resp.status_code == 401
