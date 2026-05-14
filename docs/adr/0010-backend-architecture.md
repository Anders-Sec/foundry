# ADR-0010 — Backend Architecture Decisions

**Date:** 2026-05-14
**Status:** Accepted

## Context

Phase 2 establishes the patterns that every future backend feature will follow. This ADR records the set of architectural decisions made in that phase as a unit so they can be reviewed and revisited together. They are not independent — they interact, and changing one often requires revisiting others.

## Decision

### App Factory Pattern

`create_app() -> FastAPI` rather than `app = FastAPI()` at module scope. Module-level state makes testing difficult (you can't reconfigure the app between tests) and multi-instance scenarios awkward. The factory accepts no arguments — it reads everything from settings — which keeps the interface simple while preserving testability via dependency overrides.

### Pydantic Settings with Startup Validation

All configuration is in `app/config.py` using `pydantic-settings`. Fields are typed; missing or invalid env vars fail at startup with a clear message. An additional runtime check refuses to start in non-development environments with a placeholder `jwt_secret`. The cost of a startup crash is zero in dev; the cost of deploying with a weak secret is unbounded.

### SQLAlchemy 2.0 Async + `expire_on_commit=False`

The entire stack is async: `create_async_engine`, `AsyncSession`, async route handlers. Mixing sync and async sessions is a class of subtle bug that is hard to detect and expensive to fix. `expire_on_commit=False` is set deliberately: SQLAlchemy's default session expiration causes attribute access after commit to trigger lazy IO, which is not possible in an async context without re-entering an event loop. This setting is the correct pattern for async SQLAlchemy and is documented here so future contributors understand it was intentional, not an oversight.

### Alembic with Async Engine

`alembic/env.py` uses `asyncio.run()` to drive migrations via the async engine, keeping the migration execution path consistent with the application path. Migrations are generated with `--autogenerate` and then reviewed by hand before committing — autogenerate is a starting point, not the truth.

### HS256 JWT — Access Token in Header, Refresh Token in httpOnly Cookie

Access tokens (15-minute TTL) travel in the `Authorization: Bearer` header. Refresh tokens (14-day TTL) travel in an `httpOnly` cookie scoped to `/api/v1/auth`. This combination:

- Prevents XSS from reading the refresh token (httpOnly)
- Prevents CSRF from using the refresh token for data requests (it's only sent to auth endpoints, not to data endpoints that take the access token in the header)
- Allows the access token to be used by non-browser API clients

Refresh tokens are rotated on every use. A stolen refresh token that has been rotated is immediately invalidated on the next legitimate use. This does not eliminate all refresh token risks but meaningfully reduces the window.

HS256 is used over RS256 because there is a single service verifying tokens. RS256 adds key management complexity for no benefit at this stage.

### `AuthProvider` Interface

Routes depend on `AuthProvider` (a Protocol), not `LocalAuthProvider`. The factory dependency `get_auth_provider()` returns `LocalAuthProvider` today. When OIDC is added, only `get_auth_provider()` changes. The application layer is already written against the interface. See ADR-0002 for the full rationale.

`AuthResult` carries only the `User`. Token issuance is the route's responsibility, not the provider's. This separation means OIDC providers (which have their own token model) don't need to adapt to Foundry's token format.

### Error Envelope

Every error response has the shape `{ "error": { "code": str, "message": str, "request_id": str | None } }`. The frontend writes one error-handling path. `RequestValidationError` (422) extends this with a `details` field. Three exception handlers cover the full space: `FoundryError` subclasses, Pydantic validation errors, and everything else (which logs the stack trace and returns a generic 500 without leaking internals).

### Structlog with Contextvars

`structlog` is configured to emit JSON in production and pretty-printed output in development. Request ID and user ID are bound to `contextvars` by middleware so every log line in a request carries them automatically without explicit threading. Stdlib logging (uvicorn, SQLAlchemy) is routed through structlog for a consistent log format.

## Explicit Non-Decisions

The following were considered and deferred. They are recorded here so future phases have a clear starting point.

| Concern | Status |
| ------- | ------ |
| Rate limiting (per-user, per-IP) | Deferred — no abuse signal yet |
| Token revocation / blocklist | Deferred — logout is soft (access token lives until expiry) |
| OpenAPI security scheme decorators | Deferred — `/docs` shows the endpoints but not the auth flow fully; acceptable for Phase 2 |
| Background tasks / Celery | Deferred — no async work needed yet |
| Redis / in-process caching | Deferred — no hot paths identified yet |
| Role-based authorization | Deferred — single role (authenticated vs. not) is sufficient through at least Phase 4 |

## Consequences

**Positive:**
- Every pattern established here (factory, settings, async session, auth interface, error envelope) is directly reusable in every future feature. The cost of following the pattern is near zero once it exists.
- Tests can override any dependency cleanly. testcontainers ensures integration tests hit a real database.
- The error envelope means the frontend never needs to special-case an endpoint's error format.

**Negative / trade-offs:**
- `expire_on_commit=False` means object state is stale after commit unless explicitly refreshed. This is the correct default for async, but it requires knowing that `session.refresh(obj)` exists when you need post-commit state.
- Soft logout means a stolen access token remains valid for up to 15 minutes after the user logs out. Acceptable for Phase 2; mitigated by the short TTL.
- HS256 means the signing key must be kept secret from all services that verify tokens. Not a constraint today (one service), but becomes one if verification is ever distributed.
