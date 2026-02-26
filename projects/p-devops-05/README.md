# Reliability Runbooks

- **Role Category:** DevOps / SRE
- **Status:** Planned

## Executive Summary
Creating standardized runbooks for on-call with graphs, queries, and decision trees per service.

## Scenario & Scope
Critical services spanning APIs, queues, and databases across regions.

## Responsibilities
- Document service overviews and owners
- Provide quick diagnostics and graphs
- Define escalation and rollback paths

## Tools & Technologies
- Grafana
- PagerDuty
- RunWhen
- Terraform
- Markdown

## Architecture Notes
Runbooks stored with code; linked dashboards auto-open with relevant variables for incidents.

## Process Walkthrough
- Interview service owners
- Document golden signals and alerts
- Publish runbooks with decision trees
- Pilot with on-call rotations

## Outcomes & Metrics
- Faster incident triage
- Consistent escalation paths
- Reduced toil via scripted diagnostics

## Evidence Links
- runbooks/p-devops-05/reliability-runbooks.md

## Reproduction Steps
- Clone the runbooks repo
- Open service pages in Grafana
- Test the diagnostic scripts

## Interview Points
- Designing actionable runbooks
- Keeping runbooks versioned with code
- Measuring runbook effectiveness
