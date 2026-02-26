# Resilience Testing Program

- **Role Category:** DevOps / SRE
- **Status:** In Progress

## Executive Summary
Standing up a resilience testing program with chaos experiments, SLOs, and automated rollbacks.

## Scenario & Scope
Microservices on Kubernetes with stateful services in managed databases.

## Responsibilities
- Defined SLOs and error budgets
- Authored chaos experiments for dependencies
- Integrated rollback automation based on KPIs

## Tools & Technologies
- LitmusChaos
- Grafana
- Prometheus
- Fluent Bit
- Terraform

## Architecture Notes
Experiments executed in non-prod first; metrics exported to Grafana; alerting tied to error budgets.

## Process Walkthrough
- Capture service level indicators
- Design chaos scenarios for dependencies
- Automate rollbacks when SLOs breach
- Review experiments in weekly ops council

## Outcomes & Metrics
- Established SLOs for five services
- Reduced outage MTTR via automated rollbacks
- Documented playbooks for repeatable chaos runs

## Evidence Links
- resilience/p-devops-02/chaos-program.md

## Reproduction Steps
- Deploy LitmusChaos and install CRDs
- Run sample experiments against staging
- Monitor SLO dashboards during tests

## Interview Points
- Running chaos safely
- Choosing SLOs and SLIs
- Automating rollback decisions
