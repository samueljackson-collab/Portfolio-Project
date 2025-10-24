# Security Test Plan Overview

This document outlines the repeatable security verification activities that accompany each portfolio project deployment.

## Scope
- Cloud infrastructure baselines (AWS Organizations, IAM, networking)
- Application services (web apps, APIs, and supporting data stores)
- Developer tooling and CI/CD pipelines

## Testing Cadence
- **Quarterly:** External vulnerability scans, dependency audits, and tabletop incident drills.
- **Bi-annually:** Third-party penetration testing engagements focused on critical services.
- **Pre-release:** Static and dynamic analysis incorporated into CI workflows for major features.

## Tooling & Automation
- Dependency review via GitHub Advanced Security and OWASP Dependency-Check.
- Infrastructure drift detection with Terraform plan pipelines and policy-as-code gates.
- Dynamic security testing via OWASP ZAP scripted scans in staging environments.

Refer to individual project folders for system-specific runbooks and acceptance criteria.
