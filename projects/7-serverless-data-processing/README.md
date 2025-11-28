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

### Containerized infrastructure workflows

Use the provided multi-stage image for SAM validation and packaging from consistent tooling:

```bash
docker build -f infrastructure/Dockerfile -t serverless-data-platform .

# Validate the SAM template with your local AWS credentials mounted read-only
docker run --rm \
  -v "$(pwd)/infrastructure:/app/infrastructure" \
  -v "$HOME/.aws:/root/.aws:ro" \
  serverless-data-platform
```

Because the container entrypoint is `sam`, you can override the command for other workflows, for example to build or package artefacts:

```bash
docker run --rm -v "$(pwd):/app" serverless-data-platform build --use-container
```

## Operations
- Observability via structured JSON logs, X-Ray traces, and CloudWatch metrics.
- Automatic retries and dead-letter queues for poison messages.
- Step Functions execution map for auditing and replay.
