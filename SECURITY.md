# Security Policy

## Supported Versions

Foundry is pre-1.0. Only the latest tagged release is supported for security fixes. There is no long-term support for older releases at this stage.

This policy will be updated at v1.0.0 when a formal support window is defined.

| Version | Supported |
| ------- | --------- |
| latest  | Yes       |
| older   | No        |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security reports.**

Use one of the following private channels:

1. **GitHub Security Advisories (preferred):** Use the "Report a vulnerability" button on the [Security tab](https://github.com/Anders-Sec/foundry/security/advisories/new) of this repository.
2. **Email:** Send a report to [security@itpluto.net](mailto:security@itpluto.net). Encrypt with PGP if you have a key for that address.

Include as much detail as you can: affected component, reproduction steps, potential impact, and any suggested mitigations.

## Response Expectations

- **Acknowledgment:** within 5 business days of receipt.
- **Disclosure timeline:** coordinated case-by-case based on severity and complexity. We will work with you to agree on a timeline before any public disclosure.
- We do not commit to specific patch timelines. As a solo-maintained project in early development, response capacity is limited but we treat security reports as the highest priority.

## Scope

**In scope:**

- Platform source code in this repository
- Official container images published by this project
- Official Helm charts published by this project

**Out of scope:**

- Third-party detection content (rules, signatures) not authored by this project
- User-supplied detections or IR documents managed through the platform
- Downstream forks or community-maintained packages
- Issues in dependencies (report those upstream; we will apply patches as they become available)

## Disclosure Policy

We follow coordinated disclosure. Please give us a reasonable window to investigate and remediate before disclosing publicly. We will credit reporters in the release notes unless you request anonymity.
