# Foundry Backend

FastAPI backend for the Foundry platform. Python 3.12, uv for dependency management.

## Stack

- **FastAPI** — API framework (app factory pattern)
- **SQLAlchemy 2.0 (async)** + **asyncpg** — ORM and PostgreSQL driver
- **Alembic** — database migrations
- **Pydantic / pydantic-settings** — schema validation and typed config
- **structlog** — structured JSON logging
- **Argon2 + PyJWT** — authentication (HS256, rotating refresh tokens)

See [ADR-0010](../docs/adr/0010-backend-architecture.md) for the full architecture rationale.

## Running Locally

```bash
make up             # start all services
make migrate        # apply migrations (run once after first up)
make seed           # insert dev data (idempotent)
make logs           # follow backend logs
make backend-shell  # open a shell inside the container
```

Backend: `http://localhost:8000`. Swagger UI: `http://localhost:8000/docs` (dev only).

## App Factory Pattern

The FastAPI instance is created by `create_app()` in `app/main.py`. Never add routes, models, or business logic to `main.py` — it is exclusively wiring: settings, middleware, exception handlers, router registration, lifespan.

To add a new endpoint:
1. Create (or find) a router in `app/routes/`.
2. Define Pydantic schemas in `app/schemas.py`.
3. Register the router in `create_app()`.

## Auth Flow

```
Client                    Backend
  |                          |
  |-- POST /auth/login ------>|
  |                    authenticate(username_or_email, password)
  |                    issue access token  (15 min, Bearer header)
  |                    issue refresh token (14 days, httpOnly cookie)
  |<-- 200 + access_token ---|
  |
  |-- GET /detections ------->|  Authorization: Bearer <access_token>
  |<-- 200 items -------------|
  |
  |-- POST /auth/refresh ----->|  Cookie: foundry_refresh=<token>
  |                    verify, rotate: new access + refresh tokens
  |<-- 200 + new_access_token-|
  |
  |-- POST /auth/logout ------>|
  |                    clear cookie (access token expires on its own)
  |<-- 204 ------------------|
```

Logout is soft — the access token is valid until its 15-minute TTL expires.

## Models and Migrations

Models live in `app/models.py` using SQLAlchemy 2.0 typed-mapped syntax.

**Adding a model or column:**
1. Edit `app/models.py`.
2. `docker compose exec backend alembic revision --autogenerate -m "describe change"`
3. Review the generated file in `alembic/versions/` — always review before committing.
4. `make migrate`
5. Commit the migration file.

**Rolling back:** `make migrate-down`

`expire_on_commit=False` is intentional for async SQLAlchemy. If you need post-commit state, call `await session.refresh(obj)`. See ADR-0010.

## Error Handling

```python
from app.errors import NotFoundError
raise NotFoundError("Detection not found")
```

Every error returns the same envelope:
```json
{ "error": { "code": "not_found", "message": "...", "request_id": "..." } }
```

## Dependency Management

```bash
docker compose exec backend uv add <package>
docker compose exec backend uv add --dev <package>
```

Always commit `uv.lock` after changing dependencies.

## Linting and Type Checking

```bash
make lint     # ruff check + mypy (in container)
make format   # ruff format + autofix (in container)
```

Config is in `pyproject.toml` under `[tool.ruff]` and `[tool.mypy]`.

## Tests

```bash
make test-backend                   # full suite
pytest tests/unit/                  # unit tests only (no DB)
pytest tests/test_auth.py -v        # single file
```

Integration tests use testcontainers (real Postgres, rolled-back transactions per test). See [ADR-0007](../docs/adr/0007-testing-strategy.md).

## Seed Data

```bash
make seed
```

Creates one admin user and three sample detections. Idempotent.

**Seeded credentials are for local development only. Never use in any deployed environment.**

- Username / email: `admin` / `admin@foundry.local`
- Password: `foundry-dev-admin` (or `FOUNDRY_SEED_ADMIN_PASSWORD` if set)

## Common Gotchas

- **`expire_on_commit=False`** — use `await session.refresh(obj)` if you need post-commit DB state.
- **Username enumeration** — `LocalAuthProvider` calls `dummy_verify()` on unknown users to equalize timing with a wrong-password response.
- **CORS with credentials** — `allow_credentials=True` requires an explicit `cors_origins` list (not `*`).
- **Cookie on localhost** — set `FOUNDRY_COOKIE_SECURE=false` in `.env` because the local frontend runs on `http://`, not `https://`.
