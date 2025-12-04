# SOC Playbook Modernization

- **Role Category:** Blue Team
- **Status:** Completed

## Executive Summary
Refreshed SOC runbooks with cloud-first detections, unified triage steps, and response automation hooks.

## Scenario & Scope
Coverage across Windows, Linux, and cloud audit logs with integration into a central SOAR.

## Responsibilities
- Mapped alerts to MITRE ATT&CK
- Defined triage decision trees
- Added SOAR automation triggers and rollbacks

## Tools & Technologies
- Sentinel
- Splunk
- SOAR
- KQL
- Sigma

## Architecture Notes
Standardized ingestion pipelines with schema validation; SOAR playbooks run in isolated worker VMs.

## Process Walkthrough
- Prioritized alerts based on threat intel
- Documented triage steps and data sources
- Automated containment for high-fidelity alerts
- Performed tabletop exercises to validate runbooks

## Outcomes & Metrics
- Reduced mean time to respond by 30%
- Unified alert taxonomy across tools
- Added rollback steps for automated actions

## Evidence Links
- runbooks/p-bt-01/soc-playbooks.md

## Reproduction Steps
- Import Sigma rules into the SIEM
- Deploy SOAR workflows via provided scripts
- Run tabletop scenarios with the sample alerts

## Interview Points
- Balancing automation with analyst oversight
- Mapping ATT&CK techniques to detection content
- Versioning and testing SOC runbooks
