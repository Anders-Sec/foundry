# Foundry

**Open-core platform for managing custom detections and incident response documentation for SOC teams.**

## What is Foundry?

Foundry is a detection engineering and incident response documentation platform built for SOC teams. It provides a single pane of glass for managing custom detections and IR runbooks — from authoring and version control through validation and deployment to your SIEM or EDR. Foundry is designed to remove the operational overhead of running a detection engineering program without a dedicated detection engineering team, giving analysts the tooling to build, test, and maintain a living detection library alongside structured IR documentation.

## Who is it for?

Foundry is built for SOC teams, security analysts, and security-focused individuals who need broader detection coverage and structured IR documentation without the cost of a dedicated detection engineering function. If you manage custom SIEM rules, write IR runbooks, or struggle to keep your detection library in sync with your environment, Foundry is built for you.

## Open-Core Model

The **platform** is Apache 2.0 — free to use, modify, redistribute, and host commercially. The detection content and IR document content are separate IP and are not bundled with the platform source code.

The open-source release ships with a **starter set** of detections and IR templates to get you running. Commercial customers receive curated content feeds with substantially deeper coverage, updated continuously as the threat landscape evolves. Both versions run on identical platform code — features land in commercial first, then flow to the open-source release on a defined cadence.

See [ADR-0001](docs/adr/0001-license-apache-2-open-core.md) and [ADR-0008](docs/adr/0008-open-core-boundary.md) for the full rationale and content boundary definition.

## Project Status

**Pre-1.0 / Early Development.** Foundry is not production-ready. The API, data model, and deployment architecture are all subject to change. Do not run this in a production environment yet.

## Quickstart

Local development bootstrap is in progress — see Phase 1. This section will be updated when the local development environment (Docker Compose, Makefile, pre-commit hooks) is available.

## Architecture Overview

Foundry is a FastAPI backend with a React frontend, backed by PostgreSQL, and deployed via Helm charts to Kubernetes. GitOps is managed with Argo CD — CI builds and pushes container images, then commits the immutable image tag to a separate `foundry-gitops` repository that Argo CD reconciles. See the ADRs in [docs/adr/](docs/adr/) for the full rationale behind each architectural decision.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines, commit conventions, and the pull request process.

## Security

To report a security vulnerability, follow the process in [SECURITY.md](SECURITY.md). Do not open a public GitHub issue for security reports.

## License

Platform source code is licensed under the [Apache License, Version 2.0](LICENSE).

Included starter content (detection rules and IR document templates) may carry a different license. The license for starter content will be documented when the content directory is added in a future phase. See [ADR-0008](docs/adr/0008-open-core-boundary.md) for the open-core content boundary definition.
