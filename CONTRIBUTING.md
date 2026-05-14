# Contributing to Foundry

Thank you for your interest in contributing to Foundry. This document covers everything you need to know before opening a PR.

## Code of Conduct

All participants are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## Reporting Bugs and Requesting Features

Use the GitHub issue templates:

- **Bug reports:** use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- **Feature requests:** use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)

For security vulnerabilities, do **not** open a public issue. Follow the process in [SECURITY.md](SECURITY.md).

## Development Environment Setup

Local development bootstrap is in progress. See the [README](README.md) quickstart section, which will be updated when the Docker Compose environment and Makefile are ready in Phase 1.

## DCO Sign-Off

Every commit must include a Developer Certificate of Origin sign-off. Add it with the `-s` flag:

```
git commit -s -m "feat: add detection list endpoint"
```

This appends `Signed-off-by: Your Name <your@email.com>` to the commit message, which constitutes your agreement with the [Developer Certificate of Origin 1.1](https://developercertificate.org). The DCO check will be enforced on pull requests (wired in Phase 5).

## Commit Message Conventions

Foundry uses [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

**Format:**

```
<type>[!]: <short description>

[optional body]

[optional footers]
```

**Allowed types:** `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `build`, `ci`, `perf`, `style`, `revert`

**Breaking changes:** append `!` after the type (e.g., `feat!: redesign detection schema`) or include a `BREAKING CHANGE:` footer.

**Scopes are not required.** Keep descriptions lowercase and imperative ("add", "fix", "remove", not "added", "fixes", "removed").

Examples:

```
feat: add detection list endpoint
fix: correct pagination offset calculation
docs: update quickstart instructions
chore: bump fastapi to 0.111.0
```

## Branch Naming

Suggested format: `<type>/<short-description>`. Examples:

- `feat/detection-list-endpoint`
- `fix/pagination-offset`
- `docs/contributing-guide`

This is encouraged but not enforced by tooling.

## Pull Request Process

1. All PRs target `main`.
2. Open a PR even for solo work — this keeps history reviewable and CI gating consistent.
3. Fill out the [PR template](.github/PULL_REQUEST_TEMPLATE.md) completely.
4. PRs must pass all required CI checks before merging (checks are added incrementally — see Phase 5).
5. **While there is a single maintainer, self-review is acceptable.** Once additional committers join, 1 approving reviewer will be required.
6. Squash or rebase before merging. Merge commits are not allowed on `main`.

## Code Style

Forward-reference to tooling configured in Phase 1: ruff and mypy for Python, eslint and prettier for TypeScript. Details will be documented when linting and formatting are configured.

## Tests

Tests are required for new backend business logic. The testing stack (pytest + testcontainers for backend, Vitest for frontend, Playwright for E2E) and the 75% backend coverage target are documented in [ADR-0007](docs/adr/0007-testing-strategy.md). Coverage gating is added in Phase 10 — see that phase for details.

## What We Will and Won't Accept

- **Bug fixes** are welcome. Open an issue first if the fix is non-trivial so we can discuss the approach.
- **Feature work** should be discussed in an issue before implementation. We want to make sure the feature fits the project direction before you invest time building it.
- **Contributions to the starter detection set** require prior discussion. The content boundary is documented in [ADR-0008](docs/adr/0008-open-core-boundary.md) — adding detection content is not the same as contributing platform code and has different acceptance criteria.
- **Dependencies:** prefer standard-library solutions and well-maintained packages. New runtime dependencies require a comment in the PR explaining the choice.
