# ADR-003: Security & Compliance Baseline

## Status
Accepted

## Context
Expanding surface area across projects introduced inconsistent credential handling and incomplete review coverage. The Master Factory summary calls for a security baseline that bakes secrets management, least privilege, SBOMs, and threat modeling into onboarding.

## Decision
Establish a mandatory security onboarding checklist that includes secret storage standards, least-privilege IAM patterns, software bill of materials generation, and lightweight threat modeling. Every project must adopt the baseline before production readiness.

## Consequences
- Security posture becomes measurable and repeatable across teams.
- Deviations are visible through checklist gaps and must be remediated before launch.
- Audit preparedness improves because artifacts are produced as part of normal delivery.

## References
- Master Factory Deliverables Summary, item 3: Security & Compliance Baseline (docs/master_factory_deliverables.md)
