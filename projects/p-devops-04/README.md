# Cost Optimization Lab

- **Role Category:** DevOps / SRE
- **Status:** Completed

## Executive Summary
Built a lab to evaluate autoscaling, rightsizing, and storage lifecycle policies with measurable savings.

## Scenario & Scope
Workloads across AWS and Azure with mixed batch and web services.

## Responsibilities
- Benchmarked autoscaling policies
- Evaluated storage lifecycle rules
- Modeled savings scenarios

## Tools & Technologies
- AWS Compute Optimizer
- Azure Advisor
- Grafana
- Karpenter
- FinOps dashboards

## Architecture Notes
Lab workloads tagged for cost tracking; dashboards aggregate costs by service and environment.

## Process Walkthrough
- Instrument workloads with cost tags
- Run autoscaling experiments
- Apply lifecycle rules to storage
- Summarize savings and recommendations

## Outcomes & Metrics
- Identified 25% compute savings
- Reduced storage spend via lifecycle rules
- Produced FinOps-ready dashboards

## Evidence Links
- finops/p-devops-04/cost-lab.md

## Reproduction Steps
- Deploy sample workloads with tags
- Run autoscaling scenarios
- Review cost dashboards and recommendations

## Interview Points
- Balancing performance and cost
- Autoscaling strategies across clouds
- Building FinOps dashboards
