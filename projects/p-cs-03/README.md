# Data Loss Prevention Rollout

- **Role Category:** Cloud Security
- **Status:** Completed

## Executive Summary
Implemented DLP controls for SaaS and cloud storage with classification, alerting, and user education.

## Scenario & Scope
Microsoft 365, Google Workspace, and S3 buckets storing regulated data.

## Responsibilities
- Classified data with sensitivity labels
- Defined DLP policies for email and storage
- Built user-friendly justifications and overrides

## Tools & Technologies
- Microsoft Purview
- Google DLP
- Amazon Macie
- KMS
- Power Automate

## Architecture Notes
Centralized DLP events forwarded to SIEM; override workflows log justifications for audit.

## Process Walkthrough
- Mapped data types to labels
- Deployed DLP policies in audit mode
- Educated users and enabled enforcement
- Monitored alerts and tuned policies

## Outcomes & Metrics
- Cut outbound sensitive emails by 70%
- Tagged 90% of S3 objects with labels
- Captured override justifications for audits

## Evidence Links
- policies/p-cs-03/dlp-rollout.md

## Reproduction Steps
- Enable labels in M365 and Workspace
- Deploy DLP policies in audit then enforce
- Review Macie findings and SIEM alerts

## Interview Points
- Balancing user productivity with DLP
- Cross-platform labeling consistency
- Handling false positives gracefully
