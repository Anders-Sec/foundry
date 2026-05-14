# ADR-0007 — Testing Strategy and Coverage Policy

**Date:** 2026-05-13
**Status:** Accepted

## Context

Foundry is a platform that SOC teams will use to manage and deploy detection logic to production SIEMs and EDRs. Bugs in the detection management layer can result in missed detections or incorrect deployments — this raises the stakes above a typical CRUD application.

At the same time, Foundry is in early development. Over-investing in test infrastructure before the core data model and APIs are stable wastes effort on tests that will be rewritten as the design evolves. The testing strategy must balance rigor against velocity.

## Decision

**Testing stack:**
- **Backend unit and integration tests:** pytest. Integration tests use testcontainers to spin up a real PostgreSQL instance — no mocking of the database layer.
- **Frontend unit tests:** Vitest.
- **End-to-end tests:** Playwright.

**Coverage target:**
- 75% line coverage on core backend business logic (detection management, IR document management, validation pipeline).
- Coverage is not enforced globally — generated code, migration files, and thin CRUD endpoints are excluded.
- Coverage gating (failing CI below the threshold) is added in Phase 10, not now.

**Test execution cadence:**
- Unit and integration tests: run on every PR.
- E2E smoke suite: run on every PR once a stable E2E suite exists (targeting Phase 7/8).
- Full E2E suite: run on every merge to `main` and before every release tag.

**Mutation testing:** deferred. Consider Mutmut for backend and Stryker for frontend once the test suite is mature (post-1.0).

**What "no mocking the database" means in practice:** integration tests that exercise business logic must use a real PostgreSQL instance via testcontainers. Mocking the database at the ORM or driver level is not acceptable for business logic tests — this restriction exists because database behavior (constraint enforcement, transaction semantics, index behavior) is part of the correctness guarantee. Unit tests that test pure functions with no database dependency may run without a database.

## Alternatives Considered

| Option | Reason rejected |
| ------ | --------------- |
| Mock the database in integration tests | Faster to set up but creates a false sense of correctness. The most damaging bugs in data platforms are often at the database interaction boundary. testcontainers adds startup time but eliminates an entire class of mock/prod divergence bugs. |
| Cypress instead of Playwright | Playwright has better multi-browser support, a more ergonomic async API, and stronger community momentum as of 2025. Cypress is a valid choice but Playwright is preferred here. |
| 100% coverage target | Unachievable and counterproductive. Forces test-writing on code that does not warrant it (generated files, simple getters). Metric gaming increases. |
| No coverage target | Without a target, coverage tends to decay as the project grows. The 75% target is a floor, not a ceiling. |
| Jest instead of Vitest | Vitest is faster and native to the Vite toolchain (which the React frontend will use). Jest requires additional configuration in a Vite project. |

## Consequences

**Positive:**
- Real database in integration tests catches constraint violations, migration issues, and ORM behavior bugs before production.
- testcontainers integration is self-contained — no shared test database infrastructure required.
- Playwright's multi-browser support means E2E tests can cover Chromium, Firefox, and WebKit with minimal additional effort.
- Deferred coverage gating means Phase 1-9 development is not blocked by a threshold that cannot yet be meaningful.

**Negative / trade-offs:**
- testcontainers integration tests are slower than mocked tests (database container startup adds seconds to each test run). Acceptable — fast feedback for unit tests, slower but correct feedback for integration tests.
- A 75% coverage target on business logic requires good test discipline. The definition of "business logic" vs. "infrastructure code" must be clear when coverage gating is added in Phase 10.

**Risks / open questions:**
- testcontainers requires Docker to be running in the CI environment. Confirm this is true in the Phase 5 CI setup.
- The coverage reporting tool (pytest-cov) and the reporting format (lcov for cross-tool compatibility) should be standardized in Phase 2 when the first tests are written.
