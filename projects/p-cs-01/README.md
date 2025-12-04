# Cloud Guardrails Blueprint

- **Role Category:** Cloud Security
- **Status:** Completed

## Executive Summary
Authored baseline guardrails for AWS, Azure, and GCP covering identity, networking, and data protection.

## Scenario & Scope
Greenfield multi-cloud foundation with centralized identity and logging.

## Responsibilities
- Mapped CIS benchmarks to cloud policies
- Built landing zone guardrails
- Published reusable policy-as-code modules

## Tools & Technologies
- Terraform
- AWS Organizations
- Azure Policy
- GCP Organization Policy
- OPA

## Architecture Notes
Guardrails enforced via org-level policies with exception workflows; logs aggregated into a security account.

## Process Walkthrough
- Defined baseline security controls
- Implemented policies via Terraform modules
- Tested enforcement with exception paths
- Documented runbooks for tenant onboarding

## Outcomes & Metrics
- Achieved 95% policy coverage for new accounts
- Reduced manual exceptions by introducing approvals
- Centralized audit logging across clouds

## Evidence Links
- guardrails/p-cs-01/policies.md

## Reproduction Steps
- Deploy the org-level Terraform stack
- Onboard a test account/subscription
- Validate policy enforcement and logging

## Interview Points
- Balancing guardrails with developer velocity
- Handling exceptions and drift
- Cross-cloud identity alignment
