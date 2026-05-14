# ADR-0006 — Contribution Model: DCO, No CLA, Pragmatic Gating

**Date:** 2026-05-13
**Status:** Accepted

## Context

Foundry is an open-source project licensed under Apache 2.0. It needs a contribution model that:

- Gives the project a clear chain of provenance for every contribution (who contributed what, and that they had the right to do so).
- Does not create unnecessary friction for contributors.
- Is operable by a solo maintainer without legal infrastructure.
- Scales gracefully when additional committers join.

The two common approaches are a Contributor License Agreement (CLA) and the Developer Certificate of Origin (DCO). The choice has implications for contributor friction, legal overhead, and the ability to relicense in the future.

## Decision

**DCO sign-off required. No CLA. No signed commits required initially.**

**Developer Certificate of Origin (DCO):**
Every commit must include `Signed-off-by: Full Name <email@example.com>` in the commit message, added via `git commit -s`. This constitutes the contributor's certification that they have the right to submit the contribution under the project's open-source license. The DCO 1.1 is the version in use.

A DCO check will be enforced on pull requests via CI (wired in Phase 5).

**No CLA:**
A CLA would require contributors to sign a separate legal document before their first contribution. CLAs require legal infrastructure to manage, create friction that discourages casual contributors, and are not necessary for Apache 2.0 — the license itself is permissive enough that a CLA provides limited additional protection for a project at this stage.

**Required approving reviews:**
- 0 while solo-maintained. The single maintainer self-reviews.
- 1 once additional regular committers join. This threshold is revisited when the first non-maintainer committer is onboarded.

**PR-based workflow for all work**, including solo work. Every change to `main` goes through a PR. This keeps history reviewable, ensures CI runs consistently, and establishes the habit before additional contributors exist.

**Signed commits:** off for now. GPG/SSH commit signing adds setup friction for contributors and is not required by the Apache 2.0 license. Revisit if supply-chain security requirements change (e.g., SLSA level requirements in Phase 11).

## Alternatives Considered

| Option | Reason rejected |
| ------ | --------------- |
| CLA (individual + corporate) | Requires legal review, a CLA signing service, and active management. Disproportionate overhead for a solo-maintained project. Discourages small contributions. |
| No provenance mechanism at all | Apache 2.0 does not strictly require contributor provenance tracking, but it is considered best practice and is likely required by enterprise procurement policies for any serious adoption. |
| Signed commits required from the start | Adds GPG/SSH setup to the contributor onboarding path. The marginal security benefit at this stage does not justify the friction. |

## Consequences

**Positive:**
- DCO is lightweight — one flag on `git commit`. Most developers who have contributed to Linux kernel or CNCF projects are already familiar with it.
- No legal infrastructure required.
- Apache 2.0 + DCO is a well-understood combination with clear precedent.
- PR-based workflow establishes good habits and a clean history before the project has multiple contributors.

**Negative / trade-offs:**
- DCO does not provide the same legal protections as a CLA. If Foundry ever needed to relicense (e.g., changing the platform license), DCO does not grant the project owner the right to do so without re-contacting contributors. This is an acceptable trade-off given the Apache 2.0 choice — the license is permissive and relicensing to something more restrictive would be contrary to the project's stated intent.
- 0 required reviews means a solo maintainer can merge their own mistakes. CI gating (Phase 5) is the practical safety net.

**Risks / open questions:**
- The DCO check in CI (Phase 5) needs to handle multi-commit PRs correctly — all commits in a PR must have the sign-off, not just the tip commit.
- When the first additional committer joins, revisit: required review count, CODEOWNERS granularity, and whether to add branch protection exceptions for specific maintainer workflows.
