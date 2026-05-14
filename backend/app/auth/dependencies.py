from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import decode_token
from app.auth.local import LocalAuthProvider
from app.auth.provider import AuthProvider
from app.database import get_session
from app.errors import AuthenticationError
from app.models import User

_bearer = HTTPBearer(auto_error=False)


def get_auth_provider(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuthProvider:
    return LocalAuthProvider(session)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    provider: Annotated[AuthProvider, Depends(get_auth_provider)],
) -> User:
    if credentials is None:
        raise AuthenticationError("Authentication required")

    claims = decode_token(credentials.credentials, expected_type="access")
    user = await provider.get_user(claims.sub)  # type: ignore[arg-type]

    if user is None or not user.is_active:
        raise AuthenticationError("User not found or inactive")

    return user


require_auth = Depends(get_current_user)
