# Project 7: Serverless Data Processing Platform

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


## Live Deployment
| Detail | Value |
| --- | --- |
| Live URL | `https://7-serverless-data-processing.staging.portfolio.example.com` |
| DNS | `7-serverless-data-processing.staging.portfolio.example.com` → `CNAME portfolio-gateway.staging.example.net` |
| Deployment environment | Staging (AWS us-east-1, containerized services; IaC in `terraform/`, `infra/`, or `deploy/` for this project) |

### Deployment automation
- **CI/CD:** GitHub Actions [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) gates builds; [`.github/workflows/deploy-portfolio.yml`](../../.github/workflows/deploy-portfolio.yml) publishes the staging stack.
- **Manual steps:** Follow the project Quick Start/Runbook instructions in this README to build artifacts, apply IaC, and validate health checks.

### Monitoring
- **Prometheus:** `https://prometheus.staging.portfolio.example.com` (scrape config: `prometheus/prometheus.yml`)
- **Grafana:** `https://grafana.staging.portfolio.example.com` (dashboard JSON: `grafana/dashboards/*.json`)

### Live deployment screenshots
![Live deployment dashboard](../../assets/screenshots/live-deployment-placeholder.svg)


## 📊 Portfolio Status Board

🟢 Done · 🟠 In Progress · 🔵 Planned

**Current Status:** 🟢 Done (Implemented)


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

## Evidence (local simulation)
The following artifacts capture the infrastructure plan, workflow execution logs, output data, and
cloud-metric charts generated in a local simulation (SAM/AWS CLI unavailable in this environment).

- Deployment plan summary: [`evidence/deployment-summary.json`](evidence/deployment-summary.json)
- Sample events used to trigger the workflow: [`evidence/sample-events.json`](evidence/sample-events.json)
- Execution logs: [`evidence/workflow-execution.log`](evidence/workflow-execution.log)
- Output data: [`evidence/workflow-output.json`](evidence/workflow-output.json)
- Metrics data: [`evidence/workflow-metrics.json`](evidence/workflow-metrics.json)
- Chart-ready CSVs:
  - Invocation count: [`evidence/invocation-count.csv`](evidence/invocation-count.csv)
  - Duration: [`evidence/duration-ms.csv`](evidence/duration-ms.csv)
  - Cost: [`evidence/cost-usd.csv`](evidence/cost-usd.csv)

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


## Code Generation Prompts

This section contains AI-assisted code generation prompts that can help you recreate or extend project components. These prompts are designed to work with AI coding assistants like Claude, GPT-4, or GitHub Copilot.

### Data Pipelines

#### 1. ETL Pipeline
```
Create a Python-based ETL pipeline using Apache Airflow that extracts data from PostgreSQL, transforms it with pandas, and loads it into a data warehouse with incremental updates
```

#### 2. Stream Processing
```
Generate a Kafka consumer in Python that processes real-time events, performs aggregations using sliding windows, and stores results in Redis with TTL
```

#### 3. Data Quality
```
Write a data validation framework that checks for schema compliance, null values, data freshness, and statistical anomalies, with alerting on failures
```

### How to Use These Prompts

1. **Copy the prompt** from the code block above
2. **Customize placeholders** (replace [bracketed items] with your specific requirements)
3. **Provide context** to your AI assistant about:
   - Your development environment and tech stack
   - Existing code patterns and conventions in this project
   - Any constraints or requirements specific to your use case
4. **Review and adapt** the generated code before using it
5. **Test thoroughly** and adjust as needed for your specific scenario

### Best Practices

- Always review AI-generated code for security vulnerabilities
- Ensure generated code follows your project's coding standards
- Add appropriate error handling and logging
- Write tests for AI-generated components
- Document any assumptions or limitations
- Keep sensitive information (credentials, keys) in environment variables
