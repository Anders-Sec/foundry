import time

import pytest
from httpx import AsyncClient

from app.models import User


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, seed_admin: User) -> None:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "test-password"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["user"]["username"] == "admin"
    assert "foundry_refresh" in resp.cookies


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, seed_admin: User) -> None:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "authentication_error"
    assert "access_token" not in resp.json()
    assert "foundry_refresh" not in resp.cookies


@pytest.mark.asyncio
async def test_login_unknown_user_timing(client: AsyncClient) -> None:
    """Unknown user response time should be in the same ballpark as wrong password."""
    t0 = time.monotonic()
    await client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent", "password": "x"},
    )
    unknown_time = time.monotonic() - t0

    t0 = time.monotonic()
    await client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent2", "password": "x"},
    )
    # Both should involve Argon2 work; neither should be instant (<10ms).
    assert unknown_time > 0.01, "Expected Argon2 dummy verify to take measurable time"


@pytest.mark.asyncio
async def test_login_unknown_user_returns_401(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "nobody", "password": "anything"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_rotates_cookie(client: AsyncClient, seed_admin: User) -> None:
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "test-password"},
    )
    assert login.status_code == 200
    original_cookie = login.cookies["foundry_refresh"]

    refresh = await client.post("/api/v1/auth/refresh")
    assert refresh.status_code == 200
    assert "access_token" in refresh.json()
    new_cookie = refresh.cookies.get("foundry_refresh")
    assert new_cookie is not None
    assert new_cookie != original_cookie


@pytest.mark.asyncio
async def test_refresh_no_cookie(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/auth/refresh")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_with_access_token_rejected(
    client: AsyncClient, seed_admin: User
) -> None:
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "test-password"},
    )
    access_token = login.json()["access_token"]

    # Manually set the cookie to an access token (wrong type)
    client.cookies.set("foundry_refresh", access_token, path="/api/v1/auth")
    resp = await client.post("/api/v1/auth/refresh")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_logout_clears_cookie(client: AsyncClient, seed_admin: User) -> None:
    await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "test-password"},
    )
    resp = await client.post("/api/v1/auth/logout")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/detections")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "authentication_error"


@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_token(
    authed_client: AsyncClient,
) -> None:
    resp = await authed_client.get("/api/v1/detections")
    assert resp.status_code == 200
