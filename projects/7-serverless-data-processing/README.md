# Project 7: Serverless Data Processing Platform

## Overview
A fully event-driven analytics pipeline built on AWS serverless services. The solution ingests high-velocity events, enforces schema validation, performs enrichment, and generates near real-time insights without managing servers.

## Phase 2 Architecture Diagram

![Serverless Data Processing – Phase 2](render locally to PNG; output is .gitignored)

- **Context**: Ingested events land in a raw S3 bucket before schema validation, enrichment, and orchestration steps route
  work across Lambdas, Step Functions, and streaming sinks.
- **Decision**: Isolate ingress, control plane, data plane, and insights boundaries so DLQ handling, observability, and
  analytics delivery can be governed independently.
- **Consequences**: Failures are contained in DLQs, curated DynamoDB tables and warehouses stay consistent, and dashboards can
  consume both real-time streams and curated stores. Keep the [Mermaid source](assets/diagrams/architecture.mmd) synchronized
  with the exported PNG.

## Deployment Variants
- **Primary:** AWS SAM template (`infrastructure/template.yaml`) that provisions APIs, Lambdas, Step Functions, DynamoDB, and CloudWatch resources.
- **Alternative 1:** Terraform stack with modules for cross-account deployment (see `infrastructure/terraform/`).
- **Alternative 2:** Azure Functions + Event Hub implementation blueprint located in `docs/azure/`.

## Running Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run validation and transformation unit tests
pytest

# Invoke the ingestion handler with sample payload
aws lambda invoke --function-name ingest --payload file://events/sample.json out.json
```

## Operations
- Observability via structured JSON logs, X-Ray traces, and CloudWatch metrics.
- Automatic retries and dead-letter queues for poison messages.
- Step Functions execution map for auditing and replay.
