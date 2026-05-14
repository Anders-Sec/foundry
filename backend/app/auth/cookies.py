from fastapi import Response

from app.config import get_settings

_COOKIE_NAME = "foundry_refresh"
_COOKIE_PATH = "/api/v1/auth"


def set_refresh_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path=_COOKIE_PATH,
        max_age=settings.jwt_refresh_token_ttl_seconds,
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=_COOKIE_NAME, path=_COOKIE_PATH)


def get_refresh_cookie_name() -> str:
    return _COOKIE_NAME
