from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

import structlog

log = structlog.get_logger()


class FoundryError(Exception):
    status_code: int = HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "internal_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(FoundryError):
    status_code = HTTP_404_NOT_FOUND
    code = "not_found"


class AuthenticationError(FoundryError):
    status_code = HTTP_401_UNAUTHORIZED
    code = "authentication_error"


class AuthorizationError(FoundryError):
    status_code = HTTP_403_FORBIDDEN
    code = "authorization_error"


class ConflictError(FoundryError):
    status_code = HTTP_409_CONFLICT
    code = "conflict"


def _error_body(code: str, message: str, request_id: str | None) -> dict:  # type: ignore[type-arg]
    return {"error": {"code": code, "message": message, "request_id": request_id}}


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


async def foundry_error_handler(request: Request, exc: FoundryError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.code, exc.message, _request_id(request)),
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "request_id": _request_id(request),
                "details": exc.errors(),
            }
        },
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    log.error("unhandled_exception", exc_info=exc, path=request.url.path)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_body(
            "internal_error",
            "An unexpected error occurred",
            _request_id(request),
        ),
    )
