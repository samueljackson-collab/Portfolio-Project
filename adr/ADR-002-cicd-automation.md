# ADR-002: CI/CD Automation & Quality Gates

## Status
Accepted

## Context
Release velocity was constrained by manual promotion steps and inconsistent validation coverage. The Master Factory guidance directs teams to standardize automated pipelines with policy-as-code gates for testing, security scanning, and artifact promotion.

## Decision
Implement a portfolio-standard CI/CD pipeline template that enforces automated testing, security scanning, and promotion rules. Pipelines must capture compliance evidence by default and block releases that do not meet gate criteria.

## Consequences
- Faster, repeatable releases with reduced environment drift.
- Compliance artifacts are generated automatically during each pipeline run.
- Exceptions require documented approvals and remediation follow-up.

## References
- Master Factory Deliverables Summary, item 2: CI/CD Automation & Quality Gates (docs/master_factory_deliverables.md)
