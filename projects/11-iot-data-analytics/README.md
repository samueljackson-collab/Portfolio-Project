# Project 11: IoT Data Ingestion & Analytics

## Overview
Edge-to-cloud ingestion stack with MQTT telemetry, AWS IoT Core integration, and TimescaleDB analytics.

## Highlights
- Device simulator generates MQTT payloads with configurable frequency.
- Stream processing with AWS IoT Rules -> Kinesis Data Firehose -> TimescaleDB.
- Grafana dashboards for anomaly detection and device health.

## Architecture
- **Context:** Field devices publish MQTT telemetry that must be securely ingested, normalized, and routed to both hot-path analytics and durable storage.
- **Decision:** Terminate device connections in IoT Core with mutual TLS, route via Rules Engine to Firehose, hydrate device twins, and land data in S3 and TimescaleDB with Lambda ETL; expose observability via Grafana and alerting hooks.
- **Consequences:** Simplifies device onboarding and replayability, but requires schema governance and cost controls for Firehose buffering and dual-path storage.

[Mermaid source](assets/diagrams/architecture.mmd) · Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

## Local Simulation
```bash
pip install -r requirements.txt
python src/device_simulator.py --device-count 10 --interval 2
```

## Cloud Deployment
Infrastructure templates for AWS CDK and Terraform are provided under `infrastructure/`.
