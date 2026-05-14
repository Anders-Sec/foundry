# ADR-0004 — Secrets Management: HashiCorp Vault

**Date:** 2026-05-13
**Status:** Accepted

## Context

Foundry requires secrets management for:

- Database credentials (PostgreSQL)
- JWT signing keys
- API keys for external integrations (SIEM connectors, threat intel feeds)
- Future: encryption keys for content at rest

Requirements:
- Works locally without a cloud account. Contributors must be able to run the full stack on a laptop.
- Works in k3d (local Kubernetes) and in a production Kubernetes cluster without code changes.
- Supports dynamic secrets and secret rotation, at least in principle.
- Does not vendor secrets into the Git repository in any form, including encrypted.
- Has a clear path to production-grade operation (cloud KMS auto-unseal, audit logging).

## Decision

**HashiCorp Vault, running in standard (non-dev) mode in all environments.**

Local and k3d environments are initialized via a bootstrap script that:
1. Initializes Vault with a single unseal key and root token (for simplicity in local dev).
2. Writes the unseal key and root token to a file named `vault-keys.json` in the project root.
3. `vault-keys.json` is gitignored and must never be committed.

The bootstrap script is idempotent — running it on an already-initialized Vault is a no-op.

**Production direction:** cloud KMS auto-unseal when external customers are involved. The specific KMS provider (AWS KMS, GCP Cloud KMS, Azure Key Vault) is not decided here — it depends on the customer's cloud environment. Vault's seal configuration is environment-specific and lives in `foundry-gitops`, not in the application source.

Application services access secrets via the Vault Agent sidecar or direct Vault API calls using AppRole authentication.

## Alternatives Considered

| Option | Reason rejected |
| ------ | --------------- |
| External Secrets Operator (ESO) with cloud secret managers | Requires a cloud account for every contributor running locally. Violates the "works without a cloud account" requirement. ESO is a strong choice for production-only secrets but cannot serve as the sole solution here. |
| Sealed Secrets (Bitnami) | Encrypts secrets in Git — does not solve rotation, and rotation requires re-encrypting and re-committing. Adds Kubeseal as a required tool. Does not scale well when secrets need to be shared across multiple services with different access policies. |
| Kubernetes Secrets (plaintext in etcd) | No encryption at rest by default. No access audit log. No rotation mechanism. Not acceptable for a security-focused product. |
| Doppler / Infisical / cloud-native secret manager | Introduces a required external SaaS dependency. Unacceptable for air-gapped deployments and for customers with data sovereignty requirements. |
| Vault in dev mode | Dev mode resets on restart and is explicitly not recommended for anything beyond initial experimentation. Running in dev mode would give contributors false confidence that their local state is persistent. |

## Consequences

**Positive:**
- Vault is the industry standard for secrets management in Kubernetes environments. Operators and security engineers are likely already familiar with it.
- Dynamic secrets (e.g., short-lived Postgres credentials via the database secrets engine) are available when needed.
- The path from local to production is configuration, not code changes.
- Audit logging is built into Vault — all secret accesses are logged.

**Negative / trade-offs:**
- Vault adds operational complexity compared to environment variables or Kubernetes Secrets. The bootstrap script must be reliable and well-documented.
- Vault itself becomes a dependency that must be running before the application can start. The local dev bootstrap must handle this ordering.
- The single-unseal-key local setup is not HA and is not suitable for production. This is acceptable for local dev and is explicitly called out in the bootstrap documentation.

**Risks / open questions:**
- The specific Vault Kubernetes auth method (AppRole vs. Kubernetes auth backend) for application service identity is an implementation detail for Phase 1/2. Kubernetes auth backend is preferred when running in-cluster.
- The bootstrap script is authored in Phase 1. It must handle Vault version pinning to avoid silent compatibility breaks.
