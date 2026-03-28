# SIEM Content as Code

- **Role Category:** Blue Team
- **Status:** Completed

## Executive Summary
Implemented version-controlled SIEM detections with CI linting, staged promotion, and automated packaging.

## Scenario & Scope
Centralized SIEM with multiple tenants and environment-specific overrides.

## Responsibilities
- Converted ad-hoc KQL queries into reusable modules
- Built CI checks for schema validation
- Created release pipeline for content promotion

## Tools & Technologies
- Azure DevOps
- KQL
- YAML
- Git
- Python

## Architecture Notes
Detection content stored in Git repo with environment overlays; CI builds signed packages deployed via API.

## Process Walkthrough
- Migrated existing queries into modules
- Added unit tests and linters for KQL
- Published signed content to staging, then production
- Monitored detections for drift and false positives

## Outcomes & Metrics
- Reduced manual deployment errors to zero
- Cut detection promotion time by 60%
- Enabled rollback via signed artifact history

## Evidence Links
- pipelines/p-bt-03/sien-content-ci.md

## Reproduction Steps
- Clone the detection repo and install dev dependencies
- Run the CI lint workflow locally
- Publish a signed content package to the staging SIEM

## Interview Points
- Versioning strategies for detection content
- Testing KQL queries before production
- Handling environment-specific overrides
