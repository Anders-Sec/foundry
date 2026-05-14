# ADR-0001 — License: Apache 2.0 with Open-Core Content Boundary

**Date:** 2026-05-13
**Status:** Accepted

## Context

Foundry needs a license that:

1. Permits free use, modification, redistribution, and commercial hosting by anyone — including MSPs and enterprises running it internally or as a managed service.
2. Does not block commercial differentiation. The business model depends on detection content and IR document feeds being a separate, licensable asset from the platform itself.
3. Is well understood by security teams and enterprises. License ambiguity creates friction in enterprise procurement; a recognized OSI-approved license removes that friction.
4. Does not require a Contributor License Agreement (CLA) to enforce downstream. CLAs add friction for contributors and require legal infrastructure to manage.

## Decision

**Platform source code is licensed under Apache License 2.0.**

The detection content, IR document templates, and any other non-platform assets shipped alongside the platform are explicitly out of scope for this license and will carry a separate license documented when the content directory is introduced.

The open-core boundary is: the platform (the system for managing, versioning, deploying, and validating detections and IR documents) is Apache 2.0. The content (what is managed) is the commercial differentiator and is not covered by this ADR.

Feature parity: both the open-source and commercial editions run on identical platform code. Commercial content feeds are the differentiator, not private platform features. Features land in the commercial edition first; they flow to open-source on a cadence to be specified in a future ADR.

## Alternatives Considered

| Option | Reason rejected |
| ------ | --------------- |
| Business Source License (BUSL) | Converts to Apache 2.0 after a delay, but is not OSI-approved and creates procurement friction. The "production use" restriction is difficult to define and enforce cleanly. |
| PolyForm Noncommercial | Blocks commercial hosting entirely, which would prevent MSPs and enterprises from running Foundry as a service. Too restrictive for the intended audience. |
| Elastic License 2.0 (ELv2) | Blocks managed service providers from offering Foundry as a service. Directly contradicts the goal of allowing commercial hosting. |
| GNU AGPL v3 | Network copyleft would require anyone offering Foundry as a service to open-source their modifications, which could deter enterprise adoption and complicates the commercial tier. |
| MIT | Permissive, but provides no patent grant. Apache 2.0 is strictly better for a project likely to interact with enterprise legal teams. |

## Consequences

**Positive:**
- Any individual, enterprise, or MSP can use and host Foundry without negotiating a license.
- No CLA required — DCO is sufficient (see ADR-0006).
- Apache 2.0 is well-understood in enterprise procurement processes.
- Patent grant gives downstream users additional protection.

**Negative / trade-offs:**
- Competitors can fork and redistribute the platform without contributing back (beyond the attribution requirement). Acceptable given that the differentiation is in content, not platform code.
- Content license is deferred — the boundary is documented in prose but not yet enforced in code structure. ADR-0008 governs this; enforcement in the repository structure comes when the content directory is added.

**Risks / open questions:**
- The cadence for flowing commercial features to open-source has not been defined. This should be addressed in a future ADR before the first commercial content feed ships.
