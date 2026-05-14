# Foundry Frontend

React + TypeScript frontend for the Foundry platform. Node 22 LTS, Vite 5, TanStack Router + Query.

## Stack

- **React 18** + **TypeScript 5** (strict mode)
- **Vite 5** — build tool and dev server
- **TanStack Router** — type-safe file-based routing (Phase 3)
- **TanStack Query** — server state management (Phase 3)
- **Vitest** + **Testing Library** — unit and component tests
- **ESLint** (flat config) + **Prettier** — linting and formatting

## Running Locally

The frontend runs inside Docker Compose. From the repo root:

```bash
make up             # start all services
make logs           # follow logs
```

The dev server is available at `http://localhost:5173`. Hot module replacement is active — changes to `src/` take effect immediately.

The container bind-mounts `./frontend` with `node_modules` in an anonymous volume, so the host and container file systems stay isolated.

## Dependency Management

```bash
# Add a runtime dependency
npm install <package>

# Add a dev dependency
npm install --save-dev <package>
```

Always commit `package-lock.json` after changing dependencies.

## Linting and Formatting

```bash
make lint           # eslint + prettier check (runs in container)
make format         # prettier write (runs in container)
```

Or directly:

```bash
npm run lint
npm run lint:fix
npm run format
npm run format:check
npm run typecheck
```

ESLint is configured in `eslint.config.js` (flat config). Prettier config is in `.prettierrc.json`.

## Tests

```bash
make test-frontend  # runs Vitest in the container
```

Or directly:

```bash
npm run test        # single run
npm run test:watch  # watch mode
```

Tests live alongside the code they test (`*.test.tsx`) or in `src/test/`. Phase 3 adds the first real component tests.

See [ADR-0007](../docs/adr/0007-testing-strategy.md) for the testing strategy.

## Environment Variables

Only `VITE_*` prefixed variables are exposed to the browser bundle. Do not put secrets or backend credentials in frontend environment variables. See `.env.example` at the repo root for the full list.
