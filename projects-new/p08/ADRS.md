# Architecture Decision Records

## ADR-001: Step Functions vs Custom Orchestration (Airflow/Temporal)

**Context:** Need workflow orchestration for multi-step ETL pipeline with error handling, retries, and state management. Files arrive asynchronously in S3 and require sequential processing (ingest → validate → transform → output).

**Decision:** Use AWS Step Functions Standard Workflows with Lambda task states.

**Alternatives:**
- Apache Airflow on ECS/EKS: Python DAGs, rich ecosystem, custom operators
- AWS Glue Workflows: Native AWS ETL service with PySpark support
- Temporal: Durable execution framework with code-as-workflow
- Custom SQS + Lambda: Simple queue-based orchestration

**Pros:**
- **Managed service:** No infrastructure to maintain (vs Airflow cluster management)
- **Visual workflow:** State machine definition viewable in console; easier debugging
- **Built-in error handling:** Retry logic, catch blocks, exponential backoff natively supported
- **Pay-per-execution:** No idle costs (vs always-on Airflow scheduler)
- **AWS integration:** Native S3/DynamoDB/Lambda integration; IAM for auth

**Cons:**
- **Vendor lock-in:** Proprietary ASL (Amazon States Language) vs portable Python DAGs
- **Limited branching logic:** Complex conditionals awkward in ASL vs imperative code
- **Cost at scale:** $25 per million state transitions (can exceed Airflow cost at very high volume)
- **Cold start latency:** Lambda cold starts add 1-3s overhead vs warm Airflow workers

**Consequences:**
- All ETL workflows defined as ASL state machines stored in `stepfunctions/` directory
- Retry/timeout policies codified in state machine definition (not Lambda code)
- Monitoring via CloudWatch metrics (ExecutionsStarted, ExecutionsFailed)
- State machine versioning via SAM/CDK; blue/green deployments for workflow changes

**Revisit Criteria:**
- If workflow complexity exceeds 50 states or requires extensive dynamic branching
- If cost exceeds $500/month (evaluate Express Workflows or Airflow)
- If team shifts to multi-cloud strategy (Temporal/Airflow more portable)

---

## ADR-002: SAM vs CDK vs Terraform for Infrastructure-as-Code

**Context:** Need to deploy Lambda functions, Step Functions, DynamoDB tables, IAM roles, S3 buckets, and EventBridge rules. Must support multi-environment deployments (dev, staging, prod) and rollback capability.

**Decision:** Use AWS SAM (Serverless Application Model) with CloudFormation.

**Alternatives:**
- AWS CDK (TypeScript/Python): Programmatic IaC with higher-level constructs
- Terraform: Multi-cloud, large community, HCL syntax
- Serverless Framework: Abstraction layer over CloudFormation with plugins

**Pros:**
- **Lambda-optimized:** Built-in packaging for Lambda functions with dependencies (sam build)
- **Local testing:** `sam local invoke` and `sam local start-api` for dev workflow
- **Simplified syntax:** Less verbose than raw CloudFormation; policy templates (S3ReadPolicy, DynamoDBCrudPolicy)
- **Native AWS:** First-class support for serverless services (Step Functions, EventBridge, API Gateway)
- **Deployment safety:** ChangeSet preview before apply; automatic rollback on failure

**Cons:**
- **AWS-only:** No multi-cloud portability (vs Terraform)
- **Less flexibility:** Constrained by SAM/CloudFormation capabilities vs CDK's programmatic constructs
- **Slower deployment:** CloudFormation can be slow for large stacks (vs Terraform's parallelism)
- **Limited abstraction:** Must still understand CloudFormation resource types (vs CDK L3 constructs)

**Consequences:**
- `template.yaml` as source of truth for infrastructure
- SAM CLI used for build, package, deploy (`sam deploy --guided`)
- Stack parameters for environment-specific config (e.g., DynamoDB billing mode, Lambda memory)
- Rollback via CloudFormation stack update with previous template
- CloudFormation drift detection run monthly to catch manual changes

**Revisit Criteria:**
- If deploying to non-AWS cloud (GCP, Azure) → migrate to Terraform
- If complex infrastructure logic needed (loops, conditionals) → evaluate CDK
- If deployment time >15 min becomes blocker → investigate Terraform or CDK

---

## ADR-003: Lambda vs AWS Glue for Data Transformation

**Context:** Transform step applies business logic to validated records (date parsing, aggregations, enrichment from external APIs). Files range from 1MB to 500MB; primarily JSON and CSV formats.

**Decision:** Use Lambda functions (Python 3.11) for transformation logic.

**Alternatives:**
- AWS Glue ETL Jobs: PySpark on managed Spark clusters
- AWS Glue DataBrew: Visual data preparation tool
- ECS/Fargate tasks: Containerized Python scripts with custom libraries
- EMR Serverless: Spark/Hive for large-scale processing

**Pros:**
- **Sub-second invocation:** Lambda starts in <1s vs Glue job cold start ~1-2 min
- **Cost-effective for small files:** Billed per 100ms vs Glue DPU-hours (min 10 min)
- **Simple deployment:** Single Python file + dependencies layer vs Glue script + Spark config
- **Fine-grained scaling:** Automatic concurrency (1000s of Lambdas) vs provisioned Glue DPUs
- **Fits Step Functions:** Native integration as task state

**Cons:**
- **Memory limit:** 10GB max (vs Glue workers with 16-64GB)
- **Execution timeout:** 15 min max (vs Glue jobs hours-long)
- **No distributed compute:** Single-node processing (vs Glue's Spark parallelism)
- **Package size limit:** 250MB unzipped (vs Glue no limit)

**Consequences:**
- Lambda handles files up to 500MB; larger files routed to Glue job (future enhancement)
- Business logic in `lambda/transform/handler.py` as pure Python (pandas, numpy)
- Dependency layers built via SAM (`sam build --use-container`) with numpy/pandas
- Performance profiled per Lambda; memory tuned (512MB-1024MB based on file size)
- If file size trends increase, evaluate streaming via Kinesis + Lambda or batch via Glue

**Revisit Criteria:**
- If median file size exceeds 1GB → migrate to Glue or EMR
- If transformation logic requires distributed joins → use Glue PySpark
- If Lambda costs exceed $200/month → batch small files or switch to Glue

---

## ADR-004: Lambda VPC Configuration (Public vs VPC with Endpoints)

**Context:** Lambda functions access S3 (raw/processed buckets), DynamoDB (metadata table), and Secrets Manager (API tokens). Security requirements: no public internet routing, encryption in transit, least privilege network access.

**Decision:** Deploy Lambdas in VPC private subnets with VPC endpoints for S3, DynamoDB, and Secrets Manager (no NAT Gateway).

**Alternatives:**
- Public Lambda (no VPC): Accesses AWS services via internet gateway
- VPC with NAT Gateway: Internet access for external APIs (e.g., geocoding service)
- Lambda@Edge: Run at CloudFront edge locations (not applicable here)

**Pros:**
- **No internet exposure:** Traffic stays within AWS network via PrivateLink
- **Cost savings:** VPC endpoints ~$7/month vs NAT Gateway ~$32/month + data transfer
- **Security compliance:** Meets requirement for no public internet routing
- **Reduced latency:** VPC endpoint traffic stays on AWS backbone (vs internet routing)

**Cons:**
- **Cold start penalty:** VPC Lambda adds 1-3s cold start for ENI attachment (mitigated by provisioned concurrency if critical)
- **Endpoint costs:** Each VPC endpoint ~$7/month (3 endpoints = $21/month)
- **No external API access:** Cannot call third-party APIs without NAT Gateway (workaround: API Gateway proxy or separate VPC-enabled Lambda)
- **Complexity:** Must manage security groups, subnet routing, endpoint policies

**Consequences:**
- Lambda functions deployed in 2 private subnets (multi-AZ for HA)
- VPC endpoints created for:
  - `com.amazonaws.us-east-1.s3` (Gateway endpoint, free)
  - `com.amazonaws.us-east-1.dynamodb` (Gateway endpoint, free)
  - `com.amazonaws.us-east-1.secretsmanager` (Interface endpoint, ~$7/month)
- Security groups allow outbound HTTPS (443) only to VPC endpoints
- VPC Flow Logs enabled for forensics (logged to S3, 7-day retention)
- If future requirement for external API access, add NAT Gateway or proxy via API Gateway

**Revisit Criteria:**
- If external API access becomes requirement → add NAT Gateway or API Gateway proxy
- If cold start latency SLA tightens (<1s) → evaluate public Lambda or provisioned concurrency
- If VPC endpoint costs exceed $50/month → re-evaluate public Lambda with IAM controls

---

## ADR-005: Step Functions Retry Strategy (Backoff & Max Attempts)

**Context:** Lambda functions may fail due to transient errors (DynamoDB throttling, network timeouts, S3 eventual consistency) or permanent errors (schema validation failures, malformed JSON). Need retry logic that handles transient errors without indefinitely retrying permanent errors.

**Decision:** Implement differentiated retry strategy in Step Functions ASL:
- **Transient errors:** Exponential backoff, 3 max attempts (States.Timeout, DynamoDB.ProvisionedThroughputExceededException, Lambda.ServiceException)
- **Permanent errors:** No retry, route to DLQ (ValidationError, SchemaError, custom application exceptions)

**Alternatives:**
- No retries: Fail fast, manual reprocessing from DLQ
- Unlimited retries: Keep retrying until success (risk of infinite loop)
- Circuit breaker: Disable workflow after N consecutive failures
- External retry queue: SQS with message delay for backoff

**Pros:**
- **Automated recovery:** Transient errors self-heal without operator intervention
- **Cost-effective:** Avoids wasting retries on permanent errors (vs blind retry)
- **Clear error routing:** Validation errors immediately to DLQ for manual review
- **Exponential backoff:** 2s, 4s, 8s delays reduce thundering herd on DynamoDB/S3

**Cons:**
- **Latency increase:** Retries add 2+4+8=14s latency for 3-attempt failure
- **Complexity in ASL:** Retry/Catch definitions verbose in state machine JSON
- **Error classification:** Must maintain list of transient vs permanent error types

**Example ASL Configuration:**
```json
{
  "Transform": {
    "Type": "Task",
    "Resource": "arn:aws:lambda:REGION:ACCOUNT:function:transform-handler",
    "Retry": [
      {
        "ErrorEquals": ["States.Timeout", "Lambda.ServiceException", "DynamoDB.ProvisionedThroughputExceededException"],
        "IntervalSeconds": 2,
        "MaxAttempts": 3,
        "BackoffRate": 2.0
      }
    ],
    "Catch": [
      {
        "ErrorEquals": ["ValidationError", "SchemaError"],
        "ResultPath": "$.error",
        "Next": "DLQRoute"
      },
      {
        "ErrorEquals": ["States.ALL"],
        "ResultPath": "$.error",
        "Next": "ErrorHandler"
      }
    ],
    "Next": "Output"
  }
}
```

**Consequences:**
- All Lambda functions must raise custom exceptions with clear error types (ValidationError vs ServiceError)
- DLQ receives only permanent errors (operator reviews, fixes schema/upstream data, replays)
- CloudWatch alarms monitor retry exhaustion (ExecutionsFailed metric)
- Quarterly review of error types; adjust retry classification as patterns emerge

**Revisit Criteria:**
- If retry latency exceeds SLA (p95 >30s) → reduce max attempts or backoff rate
- If DLQ depth grows >100 messages/day → investigate upstream data quality
- If new transient error types emerge → update retry ErrorEquals list

---

## ADR-006: DynamoDB Billing Mode (On-Demand vs Provisioned)

**Context:** Metadata table stores ETL execution state (file name, timestamp, status, error message, processing duration). Write traffic: 100-500 writes/min (spiky, correlated with S3 file uploads). Read traffic: minimal (only for debugging/reporting).

**Decision:** Use DynamoDB On-Demand billing mode.

**Alternatives:**
- Provisioned capacity with auto-scaling: Set baseline RCU/WCU, scale based on utilization
- Reserved capacity: Commit to baseline RCU/WCU for 1-3 year discount

**Pros:**
- **No capacity planning:** Auto-scales to handle spikes (no manual tuning)
- **Cost-effective for spiky workload:** Pay only for requests (vs over-provisioned capacity sitting idle)
- **No throttling risk:** On-demand handles sudden 2x traffic without pre-scaling
- **Simpler operations:** No alarms/auto-scaling policies to maintain

**Cons:**
- **Higher cost at sustained high throughput:** On-demand ~5x more expensive than provisioned for steady 24/7 load
- **No reserved capacity discount:** Cannot commit to savings plan

**Cost Analysis:**
- Provisioned: 100 WCU * $0.00065/hr * 730 hrs/month = $47/month + auto-scaling overhead
- On-Demand: 500 writes/min * 60 min/hr * 24 hr/day * 30 days = 21.6M writes * $1.25 per million = $27/month
- **On-Demand is 40% cheaper for current workload due to spiky pattern**

**Consequences:**
- DynamoDB table configured with BillingMode: PAY_PER_REQUEST
- No auto-scaling alarms required
- Monthly cost review to detect if traffic pattern becomes sustained (re-evaluate provisioned)
- TTL enabled (180-day expiration) to avoid storage cost growth

**Revisit Criteria:**
- If sustained write throughput >1000 writes/min for 24/7 → evaluate provisioned with reserved capacity
- If monthly cost exceeds $100 → run cost calculator for provisioned vs on-demand
- If read-heavy workload emerges (e.g., dashboard queries) → consider DAX caching

---

## ADR-007: Cost Control Strategy (Budgets, Tagging, Rightsizing)

**Context:** Serverless architecture costs can grow unpredictably with increased usage (Lambda invocations, Step Functions state transitions, S3 storage). Need proactive cost management to stay within $500/month budget.

**Decision:** Implement multi-layered cost control:
1. AWS Budgets with alerts at 80%/100% thresholds
2. Mandatory resource tagging (Environment, Owner, CostCenter)
3. Quarterly rightsizing reviews (Lambda memory, S3 lifecycle, DynamoDB TTL)
4. ARM64 Lambdas for 20% compute savings

**Alternatives:**
- Reactive monitoring: Wait for bill, investigate overruns retroactively
- Hard limits: Lambda reserved concurrency caps (risks dropped events)
- Separate AWS accounts per environment (improved isolation but more overhead)

**Pros:**
- **Proactive alerts:** Catch budget overruns before end of month
- **Cost attribution:** Tagging enables Cost Explorer grouping by team/project
- **Continuous optimization:** Quarterly reviews prevent cost drift
- **Proven savings:** ARM64 saves 20% on Lambda compute with zero code changes

**Cons:**
- **Operational overhead:** Tagging discipline, quarterly review meetings
- **False positives:** Budget alerts during legitimate traffic spikes
- **ARM64 limitations:** Some libraries incompatible (e.g., compiled C extensions)

**Implementation:**
```bash
# Create budget with SNS alerts
aws budgets create-budget \
  --account-id ACCOUNT_ID \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json

# Enforce tagging via SAM template
Tags:
  Environment: !Ref EnvironmentParameter  # dev/staging/prod
  Owner: data-engineering
  CostCenter: CC-12345

# Migrate Lambdas to ARM64
Architectures:
  - arm64
```

**Consequences:**
- All resources tagged before deployment (SAM validation enforces)
- Monthly Cost Explorer report generated first Monday of month
- Quarterly optimization sprints scheduled (review Lambda memory, S3 lifecycle, DynamoDB on-demand vs provisioned)
- ARM64 Lambda default for new functions (x86_64 only if library incompatibility)

**Revisit Criteria:**
- If monthly cost exceeds budget by >20% for 2 consecutive months → investigate anomaly or increase budget
- If tagging compliance <95% → add enforcement via CloudFormation hooks or OPA policies
- If ARM64 compatibility issues arise → maintain allowlist of x86_64-only functions
