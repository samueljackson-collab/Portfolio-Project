# Cloud Security Monitoring Fabric

- **Role Category:** Cloud Security
- **Status:** Planned

## Executive Summary
Designing unified cloud monitoring with event hubs, schema normalization, and golden signals for security.

## Scenario & Scope
Multi-cloud log aggregation with detections for identity, network, and data access.

## Responsibilities
- Define canonical schemas for audit logs
- Build ingestion pipelines with buffering
- Publish golden signals dashboards

## Tools & Technologies
- Event Hub
- Kinesis
- Pub/Sub
- Fluent Bit
- BigQuery

## Architecture Notes
Hub-and-spoke log ingestion with buffering; normalization via stream processors; storage in data lake with tiered retention.

## Process Walkthrough
- Survey cloud audit sources
- Implement streaming normalization
- Publish metrics and dashboards
- Pilot detections and alert routing

## Outcomes & Metrics
- Unified schema for 12 log types
- Reduced ingestion failures via buffering
- Published actionable golden signals

## Evidence Links
- designs/p-cs-05/monitoring-fabric.md

## Reproduction Steps
- Deploy the event hub stack
- Connect cloud audit sources
- Run sample normalization jobs

## Interview Points
- Why normalization matters for multi-cloud
- Buffering strategies for log spikes
- Golden signals for security telemetry
