# Incident Response Playoff

- **Role Category:** Blue Team
- **Status:** Planned

## Executive Summary
Designing a gamified IR exercise that pits teams against live-fire scenarios with measured MTTR targets.

## Scenario & Scope
Simulated ransomware across mixed Windows/Linux estate with cloud workloads.

## Responsibilities
- Author inject timeline and artifacts
- Define scoring tied to MTTR and containment
- Provide post-incident review templates

## Tools & Technologies
- Velociraptor
- Azure Sentinel
- Ansible
- Caldera
- Slack bots

## Architecture Notes
Exercise lab isolated via virtualization; snapshot/restore enabled for repeatability and safety.

## Process Walkthrough
- Prepare lab images and data sets
- Execute injects via automation scripts
- Score responses and track timelines
- Facilitate post-incident reviews

## Outcomes & Metrics
- Baseline MTTR benchmarks for ransomware cases
- Standardized after-action reporting
- Improved collaboration runbooks across teams

## Evidence Links
- exercises/p-bt-05/ir-playoff.md

## Reproduction Steps
- Spin up the lab with provided scripts
- Run the inject automation
- Record response times and compare to benchmarks

## Interview Points
- Designing safe yet realistic IR exercises
- Metrics that matter beyond MTTR
- Automating injects and resets
