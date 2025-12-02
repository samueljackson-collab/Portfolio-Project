# Project 4: DevSecOps Pipeline

Security-first CI pipeline with SBOM generation, container scanning, and policy checks.

## Contents
- `pipelines/github-actions.yaml` — orchestrates build, security scanning, and deployment gates.

## Phase 1 Architecture Diagram

Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

- **Context**: Every PR triggers sequential SAST, secrets scanning, SCA/SBOM creation, and ZAP DAST before artifacts move to a signed registry.
- **Decision**: Split developer activity, security controls, and release gates into distinct trust zones so policy evaluation can halt deployments without blocking code iteration.
- **Consequences**: Security findings are centralized as SARIF reports, and OPA gating keeps runtime promotions aligned to approved artifacts. Maintain the [Mermaid source](assets/diagrams/architecture.mmd) with any pipeline changes.
