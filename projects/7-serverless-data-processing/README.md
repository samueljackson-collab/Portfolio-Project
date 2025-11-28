# Project 7: Serverless Data Processing Platform

## Overview
A fully event-driven analytics pipeline built on AWS serverless services. The solution ingests high-velocity events, enforces schema validation, performs enrichment, and generates near real-time insights without managing servers.

## Architecture
```mermaid
digraph G {
  rankdir=LR
  API [label="API Gateway", shape=box]
  S3 [label="Raw Event Bucket", shape=box]
  LambdaIngest [label="Ingestion Lambda", shape=component]
  StepFn [label="Step Functions Workflow", shape=folder]
  Dynamo [label="Curated DynamoDB", shape=cylinder]
  LambdaAnalytics [label="Analytics Lambda", shape=component]
  QuickSight [label="QuickSight Dashboards", shape=box]

  API -> LambdaIngest
  S3 -> LambdaIngest
  LambdaIngest -> StepFn
  StepFn -> Dynamo
  StepFn -> LambdaAnalytics
  LambdaAnalytics -> QuickSight
}
```

## Deployment Variants
- **Primary:** AWS SAM template [`infrastructure/template.yaml`](infrastructure/template.yaml) that provisions APIs, Lambdas, Step Functions, DynamoDB, and CloudWatch resources.
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

## Operations & Tooling
- Application logic in [`src/lambda_pipeline.py`](src/lambda_pipeline.py) with tests in [`tests/test_lambda_pipeline.py`](tests/test_lambda_pipeline.py).
- CI pipeline [`./.github/workflows/ci.yml`](.github/workflows/ci.yml) running pytest and linting hooks.
- Monitoring alerts for serverless primitives in [`monitoring/alerts.yml`](monitoring/alerts.yml).
- Deployment scripts in [`scripts/deploy_sam.sh`](scripts/deploy_sam.sh) and operational playbook in [`RUNBOOK.md`](RUNBOOK.md).
