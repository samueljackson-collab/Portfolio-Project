# BCP/DR Program

- **Role Category:** GRC
- **Status:** Planned

## Executive Summary
Building a business continuity and disaster recovery program with impact analysis and test cycles.

## Scenario & Scope
Critical customer-facing services with dependencies on cloud infrastructure and third parties.

## Responsibilities
- Conduct business impact analysis
- Define RTO/RPO targets
- Schedule tabletop and technical tests

## Tools & Technologies
- BIA templates
- Runbooks
- Tabletop playbooks
- Terraform
- AWS/Azure

## Architecture Notes
BCP artifacts stored centrally; DR tests follow standard scenarios with evidence capture for auditors.

## Process Walkthrough
- Interview service owners for BIA
- Document dependencies and targets
- Plan and execute DR tests
- Capture findings and improvements

## Outcomes & Metrics
- Defined RTO/RPO per service
- Scheduled quarterly DR tests
- Improved readiness documentation

## Evidence Links
- dr/p-grc-05/bcp-program.md

## Reproduction Steps
- Run the BIA workshop
- Document service dependencies
- Execute the DR test plan

## Interview Points
- Structuring BCP/DR programs
- Measuring readiness
- Communicating with stakeholders
