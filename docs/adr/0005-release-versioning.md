# ADR-0005 — Release and Versioning: SemVer with Conventional Commits

**Date:** 2026-05-13
**Status:** Accepted

## Context

Foundry needs a versioning scheme and release process that:

- Communicates intent clearly to operators: is this a safe upgrade, or does it require migration steps?
- Is automatable from the commit history when the project is mature enough to warrant it.
- Does not require release infrastructure that doesn't exist yet (CI doesn't exist until Phase 5; release automation doesn't exist until Phase 12).
- Integrates cleanly with Helm chart versioning.

## Decision

**Semantic Versioning (SemVer) with `0.x.y` pre-1.0 versioning.**

Version format: `MAJOR.MINOR.PATCH`

- `0.x.y` during pre-1.0 development. Minor version bumps (`0.x`) may include breaking changes during this period — this is standard SemVer pre-1.0 behavior and is communicated explicitly in the README.
- `1.0.0` when the API is stable enough to make backward compatibility guarantees.

**Tagging:** manual git tags in early phases (`git tag -a v0.1.0 -m "..."` with DCO sign-off on the tag commit). Tags follow the `vMAJOR.MINOR.PATCH` format.

**release-please:** adopt `release-please` once Conventional Commits are consistently used across the project and CI (Phase 5) is stable. `release-please` reads the commit history to determine the next version and generates a changelog automatically. Target adoption: Phase 12.

**Helm chart versioning:**
- `chart.version` in `Chart.yaml` tracks the chart's own version (changes when chart templates or values change).
- `chart.appVersion` points to the matching application release tag (e.g., `v0.1.0`).
- Container images are tagged with both the release tag and the full git SHA. The git SHA tag is what Argo CD uses in GitOps (see ADR-0003); the version tag is the human-facing reference.

**No calendar versioning.** SemVer communicates upgrade safety in a way CalVer does not.

## Alternatives Considered

| Option | Reason rejected |
| ------ | --------------- |
| Calendar versioning (CalVer) | Does not communicate breaking change risk. An operator cannot tell from `2025.11` vs `2025.12` whether the upgrade is safe. |
| release-please from day one | CI does not exist yet. release-please requires a working CI pipeline. Forcing it in Phase 0 would add infrastructure without benefit. |
| No formal versioning until 1.0 | Operators running pre-1.0 releases still need a stable reference point for support, changelogs, and image tags. Manual tags satisfy this without automation overhead. |

## Consequences

**Positive:**
- SemVer is universally understood. Operators know what a minor vs. patch bump means.
- Manual tagging in early phases has zero infrastructure requirements.
- The path to automated releases (release-please) is documented and the commit convention prerequisite (Conventional Commits) is already established.
- Helm chart versioning is decoupled from application versioning, which allows chart improvements without forcing an application release.

**Negative / trade-offs:**
- Manual tagging requires discipline — a missed or mis-tagged release creates confusion in the changelog and image registry.
- Pre-1.0 breaking changes in minor versions must be clearly communicated in release notes; the version number alone is insufficient warning.

**Risks / open questions:**
- The changelog format and release note template are not defined here. Define them before the first tagged release.
- The container registry (GitHub Container Registry at `ghcr.io/anders-sec/`) is assumed but not formally confirmed. Confirm before Phase 5 wires CI.
