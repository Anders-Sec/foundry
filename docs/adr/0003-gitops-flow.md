# ADR-0003 — GitOps Flow: CI Commits Image Tags to a Separate GitOps Repo

**Date:** 2026-05-13
**Status:** Accepted

## Context

Foundry needs a deployment model that:

- Gives a clear audit trail of what is running in each environment and why.
- Supports multiple environments (local k3d, staging, production) with different promotion gates.
- Is reproducible — any cluster can be rebuilt from the repository state.
- Is understandable to contributors without deep Kubernetes or GitOps expertise.
- Does not require Argo CD to have write access to the application source repository.

The decision also needs to be made before Phase 6, where `foundry-gitops` is bootstrapped, so that the CI pipeline (Phase 5) knows what it is building toward.

## Decision

**CI builds and pushes container images tagged with the immutable git SHA. CI then commits the new image tag to a separate `foundry-gitops` repository. Argo CD watches `foundry-gitops` and reconciles the cluster state to match.**

The flow is:

1. A PR is merged to `main` in `foundry`.
2. CI builds a container image and tags it with the full git SHA (e.g., `ghcr.io/anders-sec/foundry-api:abc1234`).
3. CI opens a commit (or a PR, depending on the environment) in `foundry-gitops` updating the image tag in the relevant Helm values file.
4. Argo CD detects the change and syncs the target environment.

Environment promotion:
- `main` → staging: automated (CI commits directly, Argo CD auto-syncs).
- staging → production: manual PR in `foundry-gitops`, reviewed and merged by the maintainer.

The `foundry-gitops` repository is created in Phase 6. This ADR establishes the contract that CI must satisfy when Phase 5 wires up the pipeline.

## Alternatives Considered

| Option | Reason rejected |
| ------ | --------------- |
| Argo CD Image Updater | Adds a controller that monitors container registries and writes back to the Git repo automatically. Obscures who changed what and why — the audit trail lives in the controller logs, not in Git. Complicates the contributor mental model by adding an invisible actor. Revisit if image promotion becomes painful. |
| Push-based deployment (CI applies directly to cluster) | No GitOps audit trail. Cluster drift is undetectable without additional tooling. Hard to reproduce after a cluster failure. |
| Single repo (application + GitOps manifests) | Argo CD would need write access to the application source repo, which creates a confusing permission boundary. Keeping manifests separate makes the deployment state a distinct, auditable artifact. |
| Flux | Functionally equivalent for this use case. Argo CD is chosen for its UI and its wider familiarity in the target SOC audience. This decision can be revisited — Flux and Argo CD are both sound choices. |

## Consequences

**Positive:**
- Every deployed state is a Git commit with a clear author, timestamp, and reason.
- Cluster reconstruction is a matter of pointing Argo CD at `foundry-gitops` and syncing.
- Staging and production promotion paths are explicit and auditable.
- CI never needs cluster credentials — it only needs write access to `foundry-gitops`.

**Negative / trade-offs:**
- Two repositories to manage. Tooling, documentation, and onboarding must account for both.
- The commit from CI into `foundry-gitops` is a form of automated write — it must use a dedicated service account (not a personal token) to keep the audit trail clean.
- If multi-environment promotion becomes complex (e.g., canary, blue-green), the manual PR model in `foundry-gitops` may become tedious. **Revisit trigger:** if promotion requires more than one manual step per release, evaluate Argo CD's ApplicationSet or rollout controllers.

**Risks / open questions:**
- The service account and token used by CI to write to `foundry-gitops` must be scoped to the minimum necessary permissions. This is a Phase 5/6 implementation detail.
- The exact Helm chart structure in `foundry-gitops` is defined in Phase 6 when the repo is bootstrapped.
