import uuid
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine
from app.errors import (
    FoundryError,
    foundry_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)
from app.logging import configure_logging
from app.routes import auth, detections, health

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    log.info(
        "foundry_starting",
        version=app.version,
        env=settings.env,
        log_level=settings.log_level,
    )
    async with engine.connect() as conn:  # type: ignore[attr-defined]
        from sqlalchemy import text
        await conn.execute(text("SELECT 1"))
    log.info("database_connectivity_verified")

    yield

    await engine.dispose()  # type: ignore[attr-defined]
    log.info("foundry_shutdown")


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    settings.assert_production_safety()

    app = FastAPI(
        title="Foundry",
        version="0.1.0",
        openapi_url="/openapi.json",
        docs_url="/docs" if settings.env != "production" else None,
        redoc_url="/redoc" if settings.env != "production" else None,
        lifespan=lifespan,
    )

    # ── Middleware (outer → inner) ────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o) for o in settings.cors_origins],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        structlog.contextvars.bind_contextvars(request_id=request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        structlog.contextvars.clear_contextvars()
        return response

    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        skip_paths = {"/healthz", "/readyz"}
        if request.url.path in skip_paths:
            return await call_next(request)

        import time
        start = time.monotonic()
        response = await call_next(request)
        duration_ms = round((time.monotonic() - start) * 1000, 1)

        log.info(
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration_ms,
        )
        return response

    # ── Exception handlers ────────────────────────────────────────────────────
    app.add_exception_handler(FoundryError, foundry_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_error_handler)

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(detections.router)

    return app


app = create_app()
