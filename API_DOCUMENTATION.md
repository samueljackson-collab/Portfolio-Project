# Portfolio API Documentation

## Overview
The portfolio site is backed by a lightweight read-only API that serves project metadata, timelines, and evidence links for the case studies highlighted in the README. This document tracks the contract for that API so the front-end and any integrations can continue to evolve even while code is being recovered from backups.

> **Note:** Historical links pointed to `https://github.com/sams-jackson/portfolio`. That repository has been archived. The live home for the API (and the rest of the portfolio assets) is documented below.

## Repository Location
The canonical repository slug for this work is [`sams-jackson/Portfolio-Project`](https://github.com/sams-jackson/Portfolio-Project). Clone or browse this repository for the latest API code, documentation, and recovery updates.

```bash
git clone https://github.com/sams-jackson/Portfolio-Project.git
cd Portfolio-Project
```

- Implementation work lands on the default branch and is promoted via pull requests. Active tasks can be tracked in the [issues queue](https://github.com/sams-jackson/Portfolio-Project/issues).
- Design discussions, change proposals, and recovery notes are collected in [repository discussions](https://github.com/sams-jackson/Portfolio-Project/discussions) while legacy artifacts are being rehydrated.

If you have bookmarked the archived slug, please update any internal documents, CI jobs, or bookmarks to the new repository URL.

## Directory & Asset Map
As of the current recovery phase, the following structure is planned inside the repository:

| Path | Purpose |
| --- | --- |
| `api/spec/` | OpenAPI definitions and shared schema fragments. |
| `api/examples/` | Canonical JSON responses exported from the running service. |
| `projects/<domain>/` | Project-specific documentation and assets linked from the API. |
| `docs/` | Higher-level runbooks and operational procedures for deploying the service. |

> These folders appear as code and evidence are restored. Refer to the repository tree for up-to-date contents.

## Versioning & Release Process
- Semantic versioning (`MAJOR.MINOR.PATCH`) is used for the API. Version tags are published in the [releases tab](https://github.com/sams-jackson/Portfolio-Project/releases) once a milestone is stabilized.
- OpenAPI files are stored next to their version (for example `api/spec/v1/openapi.yaml`). Clients should pin to a specific version to avoid unexpected breaking changes.
- Legacy v0 endpoints from the archived repository will be recreated in this project under the `/v0` namespace until all clients transition to `v1`.

## Endpoint Summary (v1)
| Endpoint | Description | Notes |
| --- | --- | --- |
| `GET /api/v1/projects` | Returns an array of portfolio projects with status indicators. | JSON structure mirrors the case studies published in the repository. |
| `GET /api/v1/projects/{id}` | Detailed narrative, evidence links, and recovery status for a specific project. | Use the slug defined in the project metadata. |
| `GET /api/v1/timeline` | Chronological feed of milestones and releases. | Intended for the public portfolio site. |
| `GET /api/v1/status` | Lightweight health probe exposing build metadata. | Safe for uptime checks; no authentication required. |

Additional endpoints (e.g., `/skills`, `/tooling`, `/availability`) will be documented as they are reintroduced.

## Authentication
The API exposes read-only data and currently requires no authentication. If authenticated endpoints are added, client credentials will be distributed via GitHub issues in the private backlog and documented in this file before public release.

## Local Development Workflow
1. Clone the repository using the slug noted above.
2. Recover the latest sample data from `api/examples/`.
3. Run the API service locally (implementation details to be documented alongside the service code as it is re-open-sourced).
4. Use the OpenAPI specification to generate typed clients or to validate new endpoints.

## Support & Contact
- File bugs or feature requests in [GitHub Issues](https://github.com/sams-jackson/Portfolio-Project/issues).
- Review upcoming work or ask migration questions in [GitHub Discussions](https://github.com/sams-jackson/Portfolio-Project/discussions).
- For private coordination, reach out through the contact links listed in the repository README.

This document will continue to be updated as more of the portfolio is restored and published under the `Portfolio-Project` slug.
