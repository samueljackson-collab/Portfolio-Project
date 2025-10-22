# Engineering Onboarding Guide

Welcome to the Portfolio Platform team! This guide walks through the first week of onboarding.

## Day 1: Access & Accounts

1. Submit hardware and access requests via ServiceNow.
2. Configure MFA following the steps in the [MFA Setup](#mfa-setup) section.
3. Join Slack channels `#portfolio-engineering`, `#portfolio-ops`, and `#portfolio-security`.

### MFA Setup

1. Log in to AWS IAM Identity Center.
2. Enroll a FIDO2 security key and authenticator app.
3. Confirm access to the `PortfolioPlatformAdmin` role.

## Day 2: Local Environment

- Install prerequisites (Terraform, kubectl, Helm, awscli, jq, flyway).
- Clone the repository and run `./scripts/deploy.sh --dry-run` to familiarize yourself with the workflow.
- Review architecture in [ARCHITECTURE.md](../ARCHITECTURE.md) and deployment steps in [DEPLOYMENT.md](../DEPLOYMENT.md).

## Day 3: Shadowing

- Pair with an on-call engineer to review active alerts in Grafana.
- Walk through [documentation/runbooks/incident-response.md](./runbooks/incident-response.md).
- Review security policies in [`security/`](../security/).

## Day 4: Hands-On Task

- Pick an onboarding issue tagged `good-first-issue`.
- Run [`scripts/smoke-test.sh`](../scripts/smoke-test.sh) against staging.
- Update `documentation/onboarding.md` with any gaps discovered.

## Day 5: Knowledge Share

- Present a 15-minute readout to the team summarizing architecture, deployment, and security workflows.
- Schedule a follow-up with the DevOps lead to discuss your first sprint goals.
