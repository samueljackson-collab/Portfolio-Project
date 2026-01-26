# P08 — Serverless Data Processing Platform with AWS Lambda and Step Functions

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


**Tagline:** Event-driven ETL platform leveraging AWS Lambda, Step Functions, and S3 for cost-efficient batch and real-time data processing with automatic retries and error handling.

## Executive Summary: Serverless Advantages
- **Cost Efficiency:** Pay-per-request pricing eliminates idle resource costs; automatic scaling means no over-provisioning.
- **Operational Simplicity:** No servers to patch or manage; AWS handles infrastructure, scaling, and availability.
- **Event-Driven Architecture:** S3 triggers and EventBridge schedules enable reactive processing without polling.
- **Built-In Resilience:** Step Functions provide orchestration with retries, error handling, and DLQ for failed workflows.

## Architecture Overview

### High-Level Flow
**Data Sources** → **S3 Raw Bucket** (trigger) → **Step Functions State Machine** → **Lambda Functions** (validate/transform/enrich) → **S3 Processed Bucket** / **DynamoDB Metadata** → **Downstream Consumers** (Analytics/ML/BI)

### Components
- **EventBridge:** Schedules batch jobs (nightly, hourly) and routes custom events to Step Functions
- **S3 Event Notifications:** Trigger state machines on object creation in raw bucket
- **Step Functions:** Orchestrates multi-step workflows with parallel processing, error handling, retries, and compensation logic
- **Lambda Functions:** Stateless compute for ingestion, validation, transformation, and output delivery
- **DynamoDB:** Stores workflow metadata (execution IDs, status, timestamps, error messages)
- **AWS Glue (Optional):** For heavy ETL transformations exceeding Lambda limits
- **CloudWatch & X-Ray:** Monitoring, logging, and distributed tracing

### Directory Layout
```
projects-new/p08/
├── README.md
├── ARCHITECTURE.md
├── TESTING.md
├── REPORT_TEMPLATES.md
├── PLAYBOOK.md
├── RUNBOOKS.md
├── SOP.md
├── METRICS.md
├── ADRS.md
├── THREAT_MODEL.md
├── RISK_REGISTER.md
├── template.yaml             # SAM template
├── lambda/
│   ├── ingest/handler.py
│   ├── validate/handler.py
│   ├── transform/handler.py
│   └── output/handler.py
├── stepfunctions/
│   └── etl_workflow.asl.json
└── ci/
    └── pipeline.yml          # GitHub Actions or GitLab CI
```

## Data Flow
1. **Ingestion:** Files land in `s3://raw-data-bucket/` triggering S3 event notification
2. **Metadata Registration:** Lambda writes record to DynamoDB tracking table (execution ID, file path, timestamp, status=PENDING)
3. **Workflow Initiation:** Step Functions execution starts with S3 event payload
4. **Validation:** Lambda validates schema, checks for required fields, routes invalid to DLQ
5. **Transformation:** Lambda applies business logic (enrichment, aggregation, format conversion)
6. **Output:** Lambda writes processed data to `s3://processed-data-bucket/` and updates DynamoDB status=COMPLETED
7. **Error Handling:** Failures trigger retries (exponential backoff); persistent failures route to DLQ with alerting

## Setup

### Prerequisites
- AWS CLI configured with appropriate credentials
- AWS SAM CLI installed (`pip install aws-sam-cli`)
- Python 3.10+ for Lambda development
- S3 buckets created (`raw-data`, `processed-data`, `error-data`)

### Deploy with SAM
```bash
cd projects-new/p08
sam build
sam deploy --guided --stack-name p08-serverless-etl --capabilities CAPABILITY_IAM
```

Follow prompts to configure parameters (bucket names, DynamoDB table, Lambda memory/timeout).

### Trigger Test Workflow
```bash
# Upload sample file to raw bucket
aws s3 cp sample-data.csv s3://raw-data-bucket/input/sample-data.csv

# Monitor execution
aws stepfunctions list-executions --state-machine-arn <arn-from-outputs>
aws stepfunctions describe-execution --execution-arn <execution-arn>

# Check CloudWatch Logs
sam logs -n IngestFunction --tail
```

## Usage

### Inspecting Workflow Status
```bash
# Query DynamoDB for recent executions
aws dynamodb query --table-name etl-metadata \
  --key-condition-expression "PK = :pk" \
  --expression-attribute-values '{":pk":{"S":"EXEC#2025-01-15"}}'

# View Step Functions execution history
aws stepfunctions get-execution-history --execution-arn <arn> --max-results 50
```

### Monitoring Throughput and Health
- **CloudWatch Metrics:** Lambda invocations, duration, errors, throttles
- **Step Functions Metrics:** Execution success/failure rate, state retries
- **X-Ray Traces:** End-to-end latency breakdown and service map

### Cost Tracking
- Tag all resources with `Project:P08` for cost allocation
- CloudWatch dashboard with estimated cost per workflow execution
- Budget alerts configured for daily/monthly thresholds

## Performance Optimization

### Lambda Tuning
- **Memory Allocation:** Test 512MB-3GB to find optimal price/performance (CPU scales with memory)
- **Cold Start Mitigation:** Use provisioned concurrency for critical paths; keep dependencies minimal
- **Batch Processing:** Process multiple records per invocation to amortize overhead

### Step Functions Optimization
- **Parallel States:** Fan-out processing for independent tasks (e.g., partition-level transforms)
- **Wait State for Rate Limiting:** Throttle API calls to downstream services
- **Service Integrations:** Direct S3/DynamoDB/SNS calls avoid Lambda wrapper overhead

### Concurrency Management
- Set reserved concurrency on critical Lambdas to prevent downstream saturation
- Monitor concurrent executions vs account limits (default 1000)

## Security & Compliance

### IAM Design
- Least-privilege IAM roles per Lambda function (read from specific S3 prefix, write to specific table)
- Step Functions execution role limited to invoking specific Lambdas and services
- Cross-account access via IAM roles with external ID for trust

### Encryption
- S3 buckets encrypted with SSE-S3 or SSE-KMS for sensitive data
- DynamoDB encryption at rest enabled
- Secrets (API keys, DB passwords) stored in Secrets Manager; retrieved via SDK

### VPC Considerations
- Lambdas accessing RDS/ElastiCache deployed in VPC with NAT Gateway for internet egress
- VPC endpoints for S3/DynamoDB to avoid NAT costs

## Disaster Recovery
- S3 versioning and cross-region replication for critical data
- Step Functions state machines versioned; rollback via CloudFormation/SAM
- DynamoDB point-in-time recovery enabled

## Hiring Manager Highlights
- **Cloud-Native Expertise:** Deep understanding of serverless patterns, AWS service integrations, and cost optimization
- **Production Rigor:** Includes error handling, retries, DLQs, monitoring, and security best practices
- **Scalability:** Handles burst traffic and large files with parallel processing and auto-scaling
- **Operational Excellence:** Runbooks, playbooks, and SOPs demonstrate real-world production support experience
