# P02 IAM Hardening Master Factory

This master factory packages P02 artifacts into an operator-friendly bundle that keeps IAM development focused on least privilege, external-access detection, and unused credential cleanup. It mirrors the P01 master pattern while emphasizing policy lifecycle automation via Access Analyzer, MFA enforcement, and continuous verification.

## Artifact Map
- `diagrams.md` — Mermaid and ASCII diagrams for system, CI/CD, and IaC flows.
- `code-prompts.md` — Prompt starter pack for policy authors, reviewers, and platform engineers.
- `testing-suite.md` — Guidance for running `make setup`, `make validate-policies`, `make policy-diff`, `make simulate`, and `make test` with IAM tooling.
- `operations.md` — Operational playbook for rollout, rollback, and access hygiene.
- `reporting.md` — Reporting hooks for surfacing Access Analyzer and MFA health.
- `observability.md` — Dashboards, alerts, and log signals tied to IAM events.
- `security.md` — Guardrails that enforce least privilege and MFA-first access.
- `risk.md` — Risk register with mitigations for policy drift and unused credentials.
- `adrs.md` — Decision log for IAM automation, MFA checks, and analyzer cadence.
- `business-narrative.md` — Executive story linking IAM hygiene to audit confidence.

## Usage
Leverage the prompts to design changes, run the testing suite for validation, and consult operations/reporting docs for rollout. Keep Access Analyzer scans and MFA enforcement wired into CI/CD to prevent privilege creep and external exposure.
