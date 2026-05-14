# Repository Configuration Reference

This document captures the GitHub repository settings for `Anders-Sec/foundry` so they can be reproduced if the repository is ever recreated. Settings that require GitHub UI or `gh` CLI actions are marked accordingly.

## Repository Settings

| Setting | Value |
| ------- | ----- |
| Visibility | Public |
| Default branch | `main` |
| Description | Open-core platform for managing custom detections and incident response documentation for SOC teams. |
| Topics | `detection-engineering`, `security`, `soc`, `incident-response`, `fastapi`, `react`, `kubernetes` |
| Discussions | Enabled (categories: General, Q&A) |
| Security Advisories / Private vulnerability reporting | Enabled |
| Wiki | Disabled (documentation lives in `docs/`) |
| Projects | Enabled as needed |

## Merge Button Options

| Setting | Value |
| ------- | ----- |
| Allow squash merging | Enabled — default message: pull request title |
| Allow merge commits | Disabled |
| Allow rebase merging | Enabled |
| Automatically delete head branches | Enabled |

## Branch Protection — `main`

Configured under **Settings → Branches → Branch protection rules** for the pattern `main`.

| Setting | Value |
| ------- | ----- |
| Require a pull request before merging | Enabled |
| Required approving reviews | 0 (solo maintainer; raise to 1 when additional committers join) |
| Dismiss stale approvals on new commits | Enabled |
| Require review from code owners | Disabled (no granular CODEOWNERS yet) |
| Require status checks to pass | Enabled |
| Require branches to be up to date | Enabled |
| Required status checks | None in Phase 0 — add lint, test, and build checks at end of Phase 5 |
| Require linear history | Enabled (enforces squash or rebase; no merge commits) |
| Require signed commits | Disabled |
| Require conversation resolution | Enabled |
| Restrict who can push | Enabled |
| Allow force pushes | Disabled |
| Allow deletions | Disabled |
| Lock branch | Disabled |

## Dependabot Configuration

Configured in `.github/dependabot.yml`. Ecosystems monitored:

| Ecosystem | Directory | Schedule | Grouping |
| --------- | --------- | -------- | -------- |
| `github-actions` | `/` | Weekly | Minor + patch grouped |
| `pip` | `/` | Weekly | Minor + patch grouped |
| `npm` | `/` | Weekly | Minor + patch grouped |
| `docker` | `/` | Weekly | Minor + patch grouped |

Dependabot alerts and security updates are enabled in repository security settings.

## CODEOWNERS

All files are currently owned by `@Anders-Sec`. Update `.github/CODEOWNERS` as sub-areas develop dedicated owners.

## Notes

- These settings were last verified: 2026-05-13
- Branch protection required checks must be revisited at the end of Phase 5 to add CI gates.
- Required approving reviews must be revisited when the first non-maintainer committer joins.
- Update this document whenever repository settings are changed.
