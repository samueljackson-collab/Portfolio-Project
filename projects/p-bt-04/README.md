# Threat Hunting Sprint

- **Role Category:** Blue Team
- **Status:** Completed

## Executive Summary
Ran a two-week hunting sprint focused on identity misuse and cloud console anomalies using hypothesis-driven hunts.

## Scenario & Scope
Identity provider logs, cloud audit trails, and VPN telemetry.

## Responsibilities
- Formulated hunting hypotheses
- Built detections for anomalous sign-ins
- Created dashboards for hunt findings

## Tools & Technologies
- Splunk
- Jupyter
- Python
- Sigma
- Okta logs

## Architecture Notes
Data lake backed by object storage; hunts executed in notebooks with saved KQL/SPL queries for reuse.

## Process Walkthrough
- Defined hunt scope and data sources
- Ran exploratory analytics and baselines
- Converted hunts into persistent detections
- Reported findings and tuned alerts

## Outcomes & Metrics
- Discovered two misconfigured admin accounts
- Built four new identity anomaly detections
- Documented baselines for VPN geolocation alerts

## Evidence Links
- hunts/p-bt-04/hunt-report.md

## Reproduction Steps
- Load the sample Okta and VPN logs
- Run the provided notebooks to compute baselines
- Deploy the Sigma-derived rules to your SIEM

## Interview Points
- Hypothesis-driven hunting
- Turning hunts into detections
- Data quality considerations for identity telemetry
