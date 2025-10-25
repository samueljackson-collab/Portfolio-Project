# Project 11: IoT Data Ingestion & Analytics

## Overview
Edge-to-cloud ingestion stack with MQTT telemetry, AWS IoT Core integration, and TimescaleDB analytics.

## Highlights
- Device simulator generates MQTT payloads with configurable frequency.
- Stream processing with AWS IoT Rules -> Kinesis Data Firehose -> TimescaleDB.
- Grafana dashboards for anomaly detection and device health.

## Local Simulation
```bash
pip install -r requirements.txt
python src/device_simulator.py --device-count 10 --interval 2
```

## Cloud Deployment
Infrastructure templates for AWS CDK and Terraform are provided under `infrastructure/`.
