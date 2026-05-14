from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID

import jwt
from pydantic import BaseModel

from app.config import get_settings
from app.errors import AuthenticationError


class TokenClaims(BaseModel):
    sub: str
    type: Literal["access", "refresh"]
    exp: datetime
    iat: datetime


def _now() -> datetime:
    return datetime.now(UTC)


def create_access_token(user_id: UUID) -> str:
    settings = get_settings()
    now = _now()
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(seconds=settings.jwt_access_token_ttl_seconds),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret.get_secret_value(),
        algorithm="HS256",
    )


def create_refresh_token(user_id: UUID) -> str:
    settings = get_settings()
    now = _now()
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(seconds=settings.jwt_refresh_token_ttl_seconds),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret.get_secret_value(),
        algorithm="HS256",
    )


def decode_token(token: str, expected_type: Literal["access", "refresh"]) -> TokenClaims:
    settings = get_settings()
    try:
        raw = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")

    if raw.get("type") != expected_type:
        raise AuthenticationError(f"Expected {expected_type} token")

    return TokenClaims(**raw)
