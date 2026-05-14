# ADR-0008 — Open-Core Boundary: Where Platform Ends and Content Begins

**Date:** 2026-05-13
**Status:** Accepted

## Context

Foundry's business model depends on a clear distinction between the platform (open-source, Apache 2.0) and the content (commercial differentiator). Without a well-defined boundary, the project risks:

- Ambiguous contributions: a contributor submits a detection rule — is that a platform contribution or a content contribution?
- IP leakage: commercial detection content accidentally ends up under Apache 2.0.
- License confusion: users unsure whether they can redistribute the starter content set.

This boundary must be defined before the first external contribution is accepted.

## Decision

**Detection rules and IR documents are content, not platform. The platform is the system for managing, versioning, deploying, and validating content.**

More specifically:

- **Platform (Apache 2.0):** The API, the data model, the frontend, the Helm charts, the CLI (if any), the validation engine, the deployment pipeline, the SIEM/EDR integration layer. Everything in this repository except the content directory.
- **Content (separate license, TBD):** Detection rules, IR document templates, runbook templates, and any other security-specific artifacts that the platform manages. These live in a designated content directory (path TBD, introduced in a future phase) and carry a separate license.

**Starter content set:** The open-source release ships with a starter set of detection rules and IR templates sufficient to demonstrate the platform's capabilities and provide immediate value to a new deployment. This starter content is free to use. The license for the starter content will be determined when the content directory is introduced.

**Detection feed feature:** The ability to ingest external detection feeds and deploy detections from them to customer environments is a platform feature and ships in both the open-source and commercial editions. The feeds themselves — the content within those feeds — may be commercial. The platform does not restrict what feeds a user can configure; it simply provides the infrastructure to consume and deploy them.

**Contribution policy for starter content:**
- Platform code contributions follow the standard process in CONTRIBUTING.md.
- Content contributions (detection rules, IR templates) require prior discussion with the maintainer. The acceptance bar is higher: content contributions affect security posture and IP boundaries, not just code quality.
- Content contributed under DCO to the starter set is accepted under the starter content license, which will be documented when the content directory is added.

## Alternatives Considered

| Option | Reason rejected |
| ------ | --------------- |
| All content is Apache 2.0 | Removes the commercial differentiation entirely. The business model does not work without a content licensing boundary. |
| Commercial-only features in the platform | Violates the open-core framing. Users would need the commercial edition to use core platform capabilities. This is the Elastic model — it creates significant community friction and has driven forks (OpenSearch). |
| No starter content in the open-source release | Without starter content, a new open-source deployment has nothing to manage. The platform's value is not visible without example content. |

## Consequences

**Positive:**
- The boundary is clear: code in this repository (outside the content directory) is Apache 2.0, full stop.
- Platform feature parity between open-source and commercial editions means the community tests the same code that commercial customers run.
- The "detection feed as a platform feature" framing correctly positions the commercial offering as a content subscription, not a software license.

**Negative / trade-offs:**
- The starter content license is deferred. There will be a period (until the content directory is introduced) where the boundary is documented but not enforced in the repository structure. This is acceptable for Phase 0.
- Managing two license regimes in one repository (even in separate directories) adds complexity for contributors and requires clear documentation.

**Risks / open questions:**
- The path and structure of the content directory must be decided before any content is committed. A future ADR will document this.
- The starter content license choice (Creative Commons, a custom license, or something else) requires input from a legal perspective before the content directory is introduced.
- The cadence for flowing commercial detection content to the open-source starter set is not defined here. This should be decided before the first commercial content feed ships.
