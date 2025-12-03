# Project 4: DevSecOps Pipeline

Security-first CI pipeline with SBOM generation, container scanning, and policy checks.

## Contents
- `pipelines/github-actions.yaml` — orchestrates build, security scanning, and deployment gates.

## Architecture Diagram

- ![DevSecOps pipeline architecture](assets/diagrams/architecture.svg)
- [Mermaid source](assets/diagrams/architecture.mmd)

**ADR Note:** Security controls run inside the CI trust boundary (SAST, SCA, secrets, SBOM, DAST) before signed artifacts are promoted to a trusted registry and admission controls enforce policy in runtime clusters.
