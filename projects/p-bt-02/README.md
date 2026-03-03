# Endpoint Telemetry Uplift

- **Role Category:** Blue Team
- **Status:** In Progress

## Executive Summary
Expanded EDR telemetry coverage for Linux servers and macOS endpoints with standardized baselines.

## Scenario & Scope
Hybrid fleet across cloud VMs and corporate laptops with varying OS baselines.

## Responsibilities
- Defined minimum viable telemetry events
- Rolled out new agent policies via MDM
- Validated detections for persistence and lateral movement

## Tools & Technologies
- Elastic Agent
- osquery
- FleetDM
- MDM
- Ansible

## Architecture Notes
Used staged rollout rings with health checks; events forward through message queue before SIEM ingestion.

## Process Walkthrough
- Captured current state of endpoint logging
- Authored baseline policies for each OS
- Piloted deployment with rollback plans
- Measured detection fidelity against atomic tests

## Outcomes & Metrics
- Expanded Linux coverage from 40% to 95%
- Standardized 25 baseline queries
- Reduced false positives through tuned rules

## Evidence Links
- dashboards/p-bt-02/endpoint-coverage.md

## Reproduction Steps
- Enroll a test device via FleetDM
- Apply the baseline policy profile
- Trigger atomic persistence tests and review alerts

## Interview Points
- How to phase agent rollouts safely
- Balancing telemetry volume with cost
- Detecting lateral movement with osquery
