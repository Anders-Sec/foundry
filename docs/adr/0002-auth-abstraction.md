# ADR-0002 — Auth Abstraction: Provider Interface from Day One

**Date:** 2026-05-13
**Status:** Accepted

## Context

Foundry needs authentication from the first phase that ships a UI. The known requirements are:

- Early phases: simple local auth for solo operators and small teams with no identity provider.
- Later phases: enterprise customers will want to bring their own identity provider. Microsoft Entra ID (formerly Azure AD) is the primary target given the SOC audience, but OIDC-generic support is desirable.
- The auth system must not become a wall-to-wall refactor when the second provider is added. The cost of getting this wrong is high: auth touches sessions, permissions, and potentially the data model.

Implementing full OIDC support in Phase 1 or 2 would be premature — there is no UI yet and no enterprise customers. But implementing local auth with no abstraction would require a painful rework later.

## Decision

**Implement an `AuthProvider` interface with `LocalAuthProvider` as the only concrete implementation in early phases.**

The interface defines the contract for:
- Authenticating a user (credential validation, returning a principal)
- Issuing and validating access tokens (JWT, short-lived)
- Issuing and validating refresh tokens (longer-lived, stored server-side)
- Revoking sessions

`LocalAuthProvider` implements this contract using:
- Argon2id for password hashing (winner of the Password Hashing Competition; preferred over bcrypt for new implementations)
- Short-lived JWT access tokens (15 minutes)
- Opaque refresh tokens stored in the database with expiry and revocation support

A future `OIDCAuthProvider` will implement the same interface, with Entra ID as the first target. The interface boundary means the application layer (endpoints, permission checks, session middleware) never references `LocalAuthProvider` directly — it only references the interface.

The provider in use is selected at startup via configuration, not at compile time.

## Alternatives Considered

| Option | Reason rejected |
| ------ | --------------- |
| Local auth only, no abstraction | Cheapest now, most expensive later. Auth is pervasive — refactoring it after the data model, permissions system, and frontend are built is a significant rework. |
| Full OIDC from day one, no local auth | No identity provider to point at during development. Forces contributors to run a local IdP (e.g., Keycloak) to do anything. Too much friction. |
| Delegate to an external auth service (Auth0, Clerk, WorkOS) | Introduces a required external SaaS dependency. Violates the self-hosted, open-source-first design intent. Unacceptable for air-gapped deployments. |
| Roll OIDC into Phase 1 alongside local auth | Premature. No enterprise customer has been defined yet. The interface approach captures the value of preparation without the cost of full implementation. |

## Consequences

**Positive:**
- Adding `OIDCAuthProvider` later is additive, not a refactor. The application layer is already written against the interface.
- Local auth is simple to run locally — no external dependencies.
- Argon2id is the current best practice for password hashing; no technical debt here.
- Session revocation is built in from the start, avoiding the JWT-cannot-be-invalidated trap.

**Negative / trade-offs:**
- The interface adds a layer of indirection in Phase 1 that has no observable benefit until a second provider exists. Slightly more code for the first implementation.
- JWT access token + opaque refresh token is more complex than session cookies alone. Justified by the API-first design (frontend and potential CLI/API consumers both need token-based auth).

**Risks / open questions:**
- The exact interface surface (method signatures, error types) will be defined in Phase 2 when auth is implemented. The interface may need adjustment once the permissions model is designed — that ADR will be authored in Phase 2.
- Argon2id tuning parameters (memory, iterations, parallelism) should be benchmarked against the target deployment hardware in Phase 2 and documented in a configuration reference.
