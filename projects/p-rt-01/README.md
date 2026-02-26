# Red Team Cloud Pivot

- **Role Category:** Red Team
- **Status:** Completed

## Executive Summary
Simulated a multi-stage intrusion from phishing to cloud pivoting to validate detection depth across SaaS and IaaS assets.

## Scenario & Scope
Assumed-compromise of a user mailbox with expansion into an Azure workload landing zone.

## Responsibilities
- Designed realistic phishing lure and payload chain
- Abused OAuth token reuse to access cloud resources
- Coordinated purple-team debrief with defenders

## Tools & Technologies
- Evilginx
- Azure CLI
- BloodHound
- KQL
- Burp Suite

## Architecture Notes
Isolated attack infrastructure in a throwaway VNet with rotating outbound IPs and strict logging to a separate SIEM tenant.

## Process Walkthrough
- Conducted controlled phishing campaign with time-boxed scope
- Harvested tokens and validated MFA resilience
- Pivoted into Azure via misconfigured app registrations
- Documented detection opportunities and compensating controls

## Outcomes & Metrics
- Reduced risky OAuth app registrations by 80%
- Implemented conditional access policies for legacy protocols
- Added KQL detections for anomalous consent grants

## Evidence Links
- reports/p-rt-01/phishing-report.pdf
- dashboards/kql-detections.md

## Reproduction Steps
- Deploy the throwaway VNet using the provided Terraform module
- Run the phishing workflow with pre-approved targets
- Review SIEM alerts generated during the exercise

## Interview Points
- Why token-based persistence is harder to detect than password reuse
- How to scope red-team exercises to protect production tenants
- Cloud-specific detections for OAuth consent abuse
