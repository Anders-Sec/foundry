import os
from uuid import uuid4

import pytest

os.environ.setdefault("FOUNDRY_DATABASE_URL", "postgresql+asyncpg://x:x@localhost/x")
os.environ.setdefault("FOUNDRY_JWT_SECRET", "test-secret-that-is-long-enough-32chars")
os.environ.setdefault("FOUNDRY_ENV", "development")

from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.errors import AuthenticationError


def test_access_token_roundtrip() -> None:
    user_id = uuid4()
    token = create_access_token(user_id)
    claims = decode_token(token, expected_type="access")
    assert str(claims.sub) == str(user_id)
    assert claims.type == "access"


def test_refresh_token_roundtrip() -> None:
    user_id = uuid4()
    token = create_refresh_token(user_id)
    claims = decode_token(token, expected_type="refresh")
    assert str(claims.sub) == str(user_id)
    assert claims.type == "refresh"


def test_access_token_rejected_as_refresh() -> None:
    token = create_access_token(uuid4())
    with pytest.raises(AuthenticationError):
        decode_token(token, expected_type="refresh")


def test_refresh_token_rejected_as_access() -> None:
    token = create_refresh_token(uuid4())
    with pytest.raises(AuthenticationError):
        decode_token(token, expected_type="access")


def test_tampered_token_rejected() -> None:
    token = create_access_token(uuid4())
    tampered = token[:-4] + "xxxx"
    with pytest.raises(AuthenticationError):
        decode_token(tampered, expected_type="access")
