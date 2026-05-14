# Foundry Backend

FastAPI backend for the Foundry platform. Python 3.12, uv for dependency management.

## Stack

- **FastAPI** — API framework
- **SQLAlchemy (async)** + **asyncpg** — ORM and PostgreSQL driver
- **Alembic** — database migrations
- **Pydantic / pydantic-settings** — schema validation and config
- **structlog** — structured logging
- **Argon2 + PyJWT** — authentication (Phase 2)

## Running Locally

The backend runs inside Docker Compose. From the repo root:

```bash
make up          # start all services
make logs        # follow backend logs
make backend-shell  # open a shell inside the container
```

The container bind-mounts `./backend`, so code changes trigger hot reload automatically.

## Dependency Management

Dependencies are managed with [uv](https://docs.astral.sh/uv/).

```bash
# Add a runtime dependency
uv add <package>

# Add a dev-only dependency
uv add --dev <package>

# Sync the virtualenv after changing pyproject.toml
uv sync
```

Always commit `uv.lock` after changing dependencies.

## Linting and Formatting

```bash
make lint        # ruff check + mypy (runs in container)
make format      # ruff format + ruff check --fix (runs in container)
```

Or directly inside the backend container:

```bash
uv run ruff check .
uv run ruff format .
uv run mypy app/
```

Ruff and mypy are configured in `pyproject.toml`.

## Tests

```bash
make test-backend   # runs pytest in the container
```

Tests live in `tests/`. Integration tests use testcontainers (a real PostgreSQL instance, not a mock). Phase 2 adds the first real tests when the app factory and models exist.

See [ADR-0007](../docs/adr/0007-testing-strategy.md) for the full testing strategy.

## Configuration

All configuration is read from environment variables via `pydantic-settings`. See `.env.example` at the repo root for the full list. The settings class is defined in `app/core/config.py` (Phase 2).
