from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response
from starlette.status import HTTP_204_NO_CONTENT

from app.auth.cookies import clear_refresh_cookie, get_refresh_cookie_name, set_refresh_cookie
from app.auth.dependencies import get_auth_provider
from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.auth.provider import AuthProvider
from app.errors import AuthenticationError
from app.schemas import LoginRequest, LoginResponse, RefreshResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

_cookie_name = get_refresh_cookie_name()


@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    response: Response,
    provider: Annotated[AuthProvider, Depends(get_auth_provider)],
) -> LoginResponse:
    result = await provider.authenticate(
        body.username, body.password.get_secret_value()
    )
    if result is None:
        raise AuthenticationError("Invalid credentials")

    access_token = create_access_token(result.user.id)
    refresh_token = create_refresh_token(result.user.id)
    set_refresh_cookie(response, refresh_token)

    return LoginResponse(access_token=access_token, user=result.user)  # type: ignore[arg-type]


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(
    response: Response,
    provider: Annotated[AuthProvider, Depends(get_auth_provider)],
    refresh_token: Annotated[str | None, Cookie(alias=_cookie_name)] = None,
) -> RefreshResponse:
    if refresh_token is None:
        raise AuthenticationError("No refresh token")

    claims = decode_token(refresh_token, expected_type="refresh")
    user = await provider.get_user(claims.sub)  # type: ignore[arg-type]

    if user is None or not user.is_active:
        clear_refresh_cookie(response)
        raise AuthenticationError("Invalid or inactive user")

    new_access = create_access_token(user.id)
    new_refresh = create_refresh_token(user.id)
    set_refresh_cookie(response, new_refresh)

    return RefreshResponse(access_token=new_access)


@router.post("/logout", status_code=HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    """Clears the refresh cookie. The access token remains valid until expiry (soft logout)."""
    clear_refresh_cookie(response)
