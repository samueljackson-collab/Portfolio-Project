# Runbook — Project 7 (Serverless Data Processing Platform)

## Overview

Production operations runbook for the Serverless Data Processing Platform. This runbook covers AWS Lambda operations, Step Functions workflows, API Gateway management, DynamoDB operations, and troubleshooting for event-driven analytics pipelines.

**System Components:**
- API Gateway (event ingestion endpoints)
- AWS Lambda Functions (ingestion, validation, transformation, analytics)
- Step Functions (orchestration workflows)
- S3 (raw event storage)
- DynamoDB (curated data store)
- CloudWatch (logs, metrics, traces)
- X-Ray (distributed tracing)
- SQS Dead Letter Queues (failed message handling)
- QuickSight (analytics dashboards)

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **API availability** | 99.9% | API Gateway 2xx response rate |
| **Event processing latency (p95)** | < 500ms | Time from API ingestion → DynamoDB write |
| **Lambda success rate** | 99.5% | Successful invocations without errors |
| **Step Functions success rate** | 98% | Successful workflow completions |
| **Data loss rate** | < 0.01% | Events not reaching DynamoDB or DLQ |
| **Analytics query latency** | < 2 seconds | QuickSight dashboard load time |

---

## Dashboards & Alerts

### Dashboards

#### CloudWatch Dashboard
```bash
# View Lambda metrics
aws cloudwatch get-dashboard --dashboard-name "ServerlessDataPipeline"

# Key metrics:
# - Lambda invocations, errors, duration, throttles
# - API Gateway 4xx, 5xx error rates, latency
# - Step Functions execution status
# - DynamoDB consumed capacity, throttles

# Access via Console:
# https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=ServerlessDataPipeline
```

#### X-Ray Service Map
```bash
# View distributed trace map
aws xray get-service-graph --start-time $(date -u -d '1 hour ago' +%s) --end-time $(date -u +%s)

# Access via Console:
# https://console.aws.amazon.com/xray/home?region=us-east-1#/service-map
```

#### Step Functions Dashboard
```bash
# List recent executions
aws stepfunctions list-executions \
  --state-machine-arn arn:aws:states:us-east-1:123456789:stateMachine:DataProcessing \
  --max-results 20

# Check execution status summary
aws stepfunctions describe-state-machine \
  --state-machine-arn arn:aws:states:us-east-1:123456789:stateMachine:DataProcessing
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | API Gateway 5xx > 5% | Immediate | Check Lambda errors, rollback deployment |
| **P0** | Lambda errors > 10% | Immediate | Investigate logs, disable traffic if needed |
| **P1** | Step Functions failures > 20% | 15 minutes | Check workflow state, investigate failed steps |
| **P1** | DLQ message count > 100 | 15 minutes | Investigate poison messages, replay if needed |
| **P2** | Lambda throttling detected | 30 minutes | Increase concurrency limits |
| **P2** | DynamoDB throttling | 30 minutes | Increase provisioned capacity or use on-demand |
| **P3** | Lambda cold start > 2s | 1 hour | Consider provisioned concurrency |

#### Alert Queries

```bash
# Check Lambda error rate
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=ingestion-lambda \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Check DLQ depth
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789/processing-dlq \
  --attribute-names ApproximateNumberOfMessages

# Check Step Functions failures
aws stepfunctions list-executions \
  --state-machine-arn arn:aws:states:us-east-1:123456789:stateMachine:DataProcessing \
  --status-filter FAILED \
  --max-results 10
```

---

## Standard Operations

### API Gateway Management

#### Deploy New API Version
```bash
# 1. Validate SAM template
cd infrastructure
sam validate

# 2. Build application
sam build

# 3. Deploy to staging
sam deploy \
  --stack-name serverless-data-pipeline-staging \
  --parameter-overrides Environment=staging \
  --capabilities CAPABILITY_IAM

# 4. Test staging endpoint
STAGING_URL=$(aws cloudformation describe-stacks \
  --stack-name serverless-data-pipeline-staging \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

curl -X POST $STAGING_URL/ingest \
  -H "Content-Type: application/json" \
  -d @../test/sample_event.json

# 5. Deploy to production
sam deploy \
  --stack-name serverless-data-pipeline-prod \
  --parameter-overrides Environment=production \
  --capabilities CAPABILITY_IAM

# 6. Verify production
PROD_URL=$(aws cloudformation describe-stacks \
  --stack-name serverless-data-pipeline-prod \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

curl -X POST $PROD_URL/ingest -d @../test/sample_event.json
```

#### Configure API Gateway Throttling
```bash
# Set usage plan limits
aws apigateway update-usage-plan \
  --usage-plan-id abc123 \
  --patch-operations \
    op=replace,path=/throttle/rateLimit,value=1000 \
    op=replace,path=/throttle/burstLimit,value=2000

# Set method throttling
aws apigateway update-stage \
  --rest-api-id xyz789 \
  --stage-name prod \
  --patch-operations \
    op=replace,path=/~1ingest/POST/throttling/rateLimit,value=500 \
    op=replace,path=/~1ingest/POST/throttling/burstLimit,value=1000

# Verify settings
aws apigateway get-stage --rest-api-id xyz789 --stage-name prod
```

### Lambda Function Operations

#### Update Lambda Function Code
```bash
# 1. Build deployment package
cd functions/ingestion
pip install -r requirements.txt -t package/
cd package && zip -r ../function.zip . && cd ..
zip -g function.zip lambda_function.py

# 2. Update function
aws lambda update-function-code \
  --function-name ingestion-lambda \
  --zip-file fileb://function.zip

# 3. Wait for update to complete
aws lambda wait function-updated \
  --function-name ingestion-lambda

# 4. Test updated function
aws lambda invoke \
  --function-name ingestion-lambda \
  --payload file://../../test/sample_event.json \
  --log-type Tail \
  output.json

# 5. Check output
cat output.json
```

#### Configure Lambda Concurrency
```bash
# Set reserved concurrency (guaranteed capacity)
aws lambda put-function-concurrency \
  --function-name ingestion-lambda \
  --reserved-concurrent-executions 100

# Set provisioned concurrency (reduce cold starts)
aws lambda put-provisioned-concurrency-config \
  --function-name ingestion-lambda \
  --provisioned-concurrent-executions 10 \
  --qualifier prod

# Check current concurrency
aws lambda get-function-concurrency \
  --function-name ingestion-lambda
```

#### View Lambda Logs
```bash
# Get recent log streams
aws logs describe-log-streams \
  --log-group-name /aws/lambda/ingestion-lambda \
  --order-by LastEventTime \
  --descending \
  --max-items 5

# Tail logs in real-time
aws logs tail /aws/lambda/ingestion-lambda --follow

# Filter logs for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/ingestion-lambda \
  --filter-pattern "ERROR" \
  --start-time $(date -u -d '1 hour ago' +%s)000

# Search for specific request ID
aws logs filter-log-events \
  --log-group-name /aws/lambda/ingestion-lambda \
  --filter-pattern "REQUEST_ID_HERE"
```

### Step Functions Management

#### Start Workflow Execution
```bash
# Start execution with input
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:us-east-1:123456789:stateMachine:DataProcessing \
  --name execution-$(date +%s) \
  --input file://input.json

# Get execution ARN from output
EXECUTION_ARN=$(aws stepfunctions start-execution ... --query 'executionArn' --output text)

# Monitor execution
aws stepfunctions describe-execution --execution-arn $EXECUTION_ARN

# Wait for completion
while true; do
  STATUS=$(aws stepfunctions describe-execution \
    --execution-arn $EXECUTION_ARN \
    --query 'status' --output text)
  echo "Status: $STATUS"
  [[ "$STATUS" == "SUCCEEDED" || "$STATUS" == "FAILED" ]] && break
  sleep 5
done
```

#### View Execution History
```bash
# Get execution history
aws stepfunctions get-execution-history \
  --execution-arn $EXECUTION_ARN \
  --max-results 100

# Filter for failed states
aws stepfunctions get-execution-history \
  --execution-arn $EXECUTION_ARN \
  --max-results 100 | \
  jq '.events[] | select(.type | contains("Failed"))'

# Get execution output
aws stepfunctions describe-execution \
  --execution-arn $EXECUTION_ARN \
  --query 'output' --output text | jq .
```

#### Stop Running Execution
```bash
# Stop execution (emergency)
aws stepfunctions stop-execution \
  --execution-arn $EXECUTION_ARN \
  --cause "Emergency stop due to data quality issue" \
  --error "DataQualityError"

# Verify stopped
aws stepfunctions describe-execution --execution-arn $EXECUTION_ARN
```

### DynamoDB Operations

#### Query Data
```bash
# Query by partition key
aws dynamodb query \
  --table-name CuratedEvents \
  --key-condition-expression "eventType = :type" \
  --expression-attribute-values '{":type":{"S":"purchase"}}'

# Query with filter
aws dynamodb query \
  --table-name CuratedEvents \
  --key-condition-expression "eventType = :type AND eventTime > :time" \
  --expression-attribute-values '{
    ":type":{"S":"purchase"},
    ":time":{"N":"'$(date -d '1 day ago' +%s)'"}
  }'

# Scan table (use sparingly)
aws dynamodb scan \
  --table-name CuratedEvents \
  --filter-expression "amount > :amt" \
  --expression-attribute-values '{":amt":{"N":"1000"}}'
```

#### Update Table Capacity
```bash
# Switch to on-demand (auto-scaling)
aws dynamodb update-table \
  --table-name CuratedEvents \
  --billing-mode PAY_PER_REQUEST

# Switch to provisioned (cost optimization)
aws dynamodb update-table \
  --table-name CuratedEvents \
  --billing-mode PROVISIONED \
  --provisioned-throughput ReadCapacityUnits=50,WriteCapacityUnits=50

# Update auto-scaling
aws application-autoscaling register-scalable-target \
  --service-namespace dynamodb \
  --resource-id table/CuratedEvents \
  --scalable-dimension dynamodb:table:WriteCapacityUnits \
  --min-capacity 5 \
  --max-capacity 100
```

#### Backup and Restore
```bash
# Create on-demand backup
aws dynamodb create-backup \
  --table-name CuratedEvents \
  --backup-name curated-events-$(date +%Y%m%d-%H%M)

# List backups
aws dynamodb list-backups --table-name CuratedEvents

# Restore from backup
aws dynamodb restore-table-from-backup \
  --target-table-name CuratedEvents-restored \
  --backup-arn arn:aws:dynamodb:us-east-1:123456789:table/CuratedEvents/backup/12345

# Enable point-in-time recovery
aws dynamodb update-continuous-backups \
  --table-name CuratedEvents \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true
```

### Dead Letter Queue Management

#### Check DLQ Messages
```bash
# Get queue depth
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789/processing-dlq \
  --attribute-names ApproximateNumberOfMessages,ApproximateNumberOfMessagesNotVisible

# Receive messages (peek)
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789/processing-dlq \
  --max-number-of-messages 10 \
  --visibility-timeout 30

# Save messages for analysis
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789/processing-dlq \
  --max-number-of-messages 10 > dlq_messages.json
```

#### Replay DLQ Messages
```bash
# Script to replay messages
cat > scripts/replay_dlq.sh << 'EOF'
#!/bin/bash
DLQ_URL="https://sqs.us-east-1.amazonaws.com/123456789/processing-dlq"
TARGET_LAMBDA="ingestion-lambda"

# Receive and process messages
while true; do
  MSG=$(aws sqs receive-message --queue-url $DLQ_URL --max-number-of-messages 1)

  if [ -z "$(echo $MSG | jq -r '.Messages[0].Body')" ]; then
    echo "No more messages"
    break
  fi

  BODY=$(echo $MSG | jq -r '.Messages[0].Body')
  RECEIPT=$(echo $MSG | jq -r '.Messages[0].ReceiptHandle')

  # Retry Lambda invocation
  aws lambda invoke \
    --function-name $TARGET_LAMBDA \
    --payload "$BODY" \
    /tmp/output.json

  if [ $? -eq 0 ]; then
    # Delete from DLQ if successful
    aws sqs delete-message --queue-url $DLQ_URL --receipt-handle "$RECEIPT"
    echo "Replayed and deleted message"
  else
    echo "Replay failed, leaving in DLQ"
  fi
done
EOF

chmod +x scripts/replay_dlq.sh
./scripts/replay_dlq.sh
```

---

## Incident Response

### Detection

**Automated Detection:**
- CloudWatch alarms for Lambda errors, throttles
- API Gateway 4xx/5xx error rate alarms
- Step Functions execution failure alarms
- DynamoDB throttling alarms
- DLQ depth alarms

**Manual Detection:**
```bash
# Check overall system health
./scripts/health_check.sh

# Check Lambda errors
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=ingestion-lambda \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Check API Gateway health
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name 5XXError \
  --dimensions Name=ApiName,Value=ServerlessDataAPI \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

### Triage

#### Severity Classification

**P0: Complete Outage**
- API Gateway returning 5xx errors > 50%
- All Lambda functions failing
- Step Functions completely unable to execute
- DynamoDB table unavailable

**P1: Degraded Service**
- Lambda error rate > 10%
- API Gateway 5xx errors > 5%
- Step Functions failure rate > 20%
- DynamoDB throttling affecting > 50% requests

**P2: Warning State**
- Lambda throttling detected
- DLQ message count increasing
- Elevated latency (p95 > 1s)
- DynamoDB capacity approaching limits

**P3: Informational**
- Occasional Lambda cold starts
- Minor latency increase
- DLQ contains < 10 messages

### Incident Response Procedures

#### P0: API Gateway 5xx Errors

**Immediate Actions (0-2 minutes):**
```bash
# 1. Check API Gateway status
aws apigateway get-rest-apis

# 2. Check backend Lambda health
aws lambda get-function --function-name ingestion-lambda

# 3. Check recent Lambda errors
aws logs tail /aws/lambda/ingestion-lambda --since 5m | grep ERROR

# 4. Emergency: Rollback to previous version
PREVIOUS_VERSION=$(aws lambda list-versions-by-function \
  --function-name ingestion-lambda \
  --query 'Versions[-2].Version' --output text)

aws lambda update-alias \
  --function-name ingestion-lambda \
  --name prod \
  --function-version $PREVIOUS_VERSION

# 5. Clear API Gateway cache
aws apigateway flush-stage-cache \
  --rest-api-id xyz789 \
  --stage-name prod
```

**Investigation (2-10 minutes):**
```bash
# Check X-Ray traces
aws xray get-trace-summaries \
  --start-time $(date -u -d '10 minutes ago' +%s) \
  --end-time $(date -u +%s) \
  --filter-expression 'error = true'

# Get trace details
TRACE_ID=$(aws xray get-trace-summaries ... --query 'TraceSummaries[0].Id' --output text)
aws xray batch-get-traces --trace-ids $TRACE_ID

# Check CloudWatch Insights
aws logs start-query \
  --log-group-name /aws/lambda/ingestion-lambda \
  --start-time $(date -u -d '10 minutes ago' +%s) \
  --end-time $(date -u +%s) \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/ | limit 20'
```

**Mitigation:**
```bash
# Option 1: Scale up Lambda concurrency
aws lambda put-function-concurrency \
  --function-name ingestion-lambda \
  --reserved-concurrent-executions 200

# Option 2: Enable throttling at API Gateway
aws apigateway update-stage \
  --rest-api-id xyz789 \
  --stage-name prod \
  --patch-operations op=replace,path=/throttle/rateLimit,value=500

# Option 3: Route traffic to backup region (if available)
# Update Route53 health check to fail over
```

#### P0: All Lambda Functions Failing

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check Lambda service health
aws health describe-events --filter eventTypeCategories=issue,accountSpecific

# 2. Check all Lambda functions
for func in ingestion-lambda transformation-lambda analytics-lambda; do
  echo "Checking $func..."
  aws lambda get-function --function-name $func
  aws logs tail /aws/lambda/$func --since 5m | head -20
done

# 3. Test function invocation
aws lambda invoke \
  --function-name ingestion-lambda \
  --payload '{"test": true}' \
  --log-type Tail \
  test_output.json

# 4. Check for account limits
aws lambda get-account-settings

# 5. Rollback all functions if recent deployment
./scripts/rollback_all_lambdas.sh
```

**Investigation:**
```bash
# Check for permission issues
aws lambda get-function --function-name ingestion-lambda \
  --query 'Configuration.Role'

aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789:role/lambda-execution-role \
  --action-names dynamodb:PutItem s3:GetObject

# Check for dependency issues
aws lambda get-function --function-name ingestion-lambda \
  --query 'Configuration.Layers'

# Check environment variables
aws lambda get-function-configuration \
  --function-name ingestion-lambda \
  --query 'Environment'
```

#### P1: Step Functions High Failure Rate

**Investigation:**
```bash
# List recent failed executions
aws stepfunctions list-executions \
  --state-machine-arn arn:aws:states:us-east-1:123456789:stateMachine:DataProcessing \
  --status-filter FAILED \
  --max-results 20

# Analyze first failure
FAILED_EXEC=$(aws stepfunctions list-executions ... --query 'executions[0].executionArn' --output text)

aws stepfunctions describe-execution --execution-arn $FAILED_EXEC

# Get failure details
aws stepfunctions get-execution-history \
  --execution-arn $FAILED_EXEC | \
  jq '.events[] | select(.type | contains("Failed"))'

# Check common failure patterns
for exec in $(aws stepfunctions list-executions --status-filter FAILED --query 'executions[*].executionArn' --output text); do
  aws stepfunctions describe-execution --execution-arn $exec --query 'cause'
done
```

**Mitigation:**
```bash
# If Lambda function issue, fix and retry
# Update Lambda function
aws lambda update-function-code --function-name transformation-lambda --zip-file fileb://fix.zip

# Restart failed executions
for exec in $(aws stepfunctions list-executions --status-filter FAILED --max-results 50 --query 'executions[*].executionArn' --output text); do
  INPUT=$(aws stepfunctions describe-execution --execution-arn $exec --query 'input')
  aws stepfunctions start-execution \
    --state-machine-arn arn:aws:states:us-east-1:123456789:stateMachine:DataProcessing \
    --input "$INPUT"
done

# If workflow definition issue, update state machine
aws stepfunctions update-state-machine \
  --state-machine-arn arn:aws:states:us-east-1:123456789:stateMachine:DataProcessing \
  --definition file://state_machine_fixed.json
```

#### P1: DLQ Message Count High

**Investigation:**
```bash
# Get DLQ depth
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789/processing-dlq \
  --attribute-names All

# Sample messages
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789/processing-dlq \
  --max-number-of-messages 10 > sample_dlq.json

# Analyze message patterns
cat sample_dlq.json | jq -r '.Messages[].Body' | jq -s 'group_by(.eventType) | map({eventType: .[0].eventType, count: length})'

# Check for poison message
cat sample_dlq.json | jq -r '.Messages[0].Body' | jq .
```

**Mitigation:**
```bash
# Option 1: Fix issue and replay all
# Fix the Lambda function
aws lambda update-function-code --function-name ingestion-lambda --zip-file fileb://fix.zip

# Replay DLQ messages
./scripts/replay_dlq.sh

# Option 2: Purge poison messages
# Move to analysis bucket first
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789/processing-dlq \
  --max-number-of-messages 10 > poison_messages.json

aws s3 cp poison_messages.json s3://analysis-bucket/dlq/$(date +%Y%m%d)/

# Purge queue
aws sqs purge-queue \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789/processing-dlq
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** 25 minutes
**Affected Component:** Lambda ingestion function

## Timeline
- 14:00: Lambda errors spiked to 15%
- 14:05: API Gateway 5xx errors detected
- 14:08: Identified code regression in recent deployment
- 14:15: Rolled back Lambda to previous version
- 14:20: Error rate returned to normal
- 14:25: Verified full recovery

## Root Cause
Null pointer exception in new validation logic

## Action Items
- [ ] Add null checks to validation logic
- [ ] Improve unit test coverage for edge cases
- [ ] Add integration tests for validation scenarios
- [ ] Update deployment checklist

EOF

# Review CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=ingestion-lambda \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum > incidents/metrics-$(date +%Y%m%d-%H%M).json
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: Lambda Timeout

**Symptoms:**
```bash
$ aws logs tail /aws/lambda/transformation-lambda --since 5m
Task timed out after 30.00 seconds
```

**Diagnosis:**
```bash
# Check function timeout setting
aws lambda get-function-configuration \
  --function-name transformation-lambda \
  --query 'Timeout'

# Check average duration
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=transformation-lambda \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average,Maximum
```

**Solution:**
```bash
# Increase timeout (max 15 minutes)
aws lambda update-function-configuration \
  --function-name transformation-lambda \
  --timeout 60

# Or optimize function code
# - Reduce batch size
# - Add pagination for large datasets
# - Move heavy processing to Step Functions
```

---

#### Issue: DynamoDB Throttling

**Symptoms:**
```bash
ProvisionedThroughputExceededException: Rate of requests exceeds the allowed throughput
```

**Diagnosis:**
```bash
# Check consumed capacity
aws dynamodb describe-table --table-name CuratedEvents \
  --query 'Table.ProvisionedThroughput'

# Check throttle metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name UserErrors \
  --dimensions Name=TableName,Value=CuratedEvents \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

**Solution:**
```bash
# Option 1: Switch to on-demand
aws dynamodb update-table \
  --table-name CuratedEvents \
  --billing-mode PAY_PER_REQUEST

# Option 2: Increase provisioned capacity
aws dynamodb update-table \
  --table-name CuratedEvents \
  --provisioned-throughput ReadCapacityUnits=100,WriteCapacityUnits=100

# Option 3: Enable auto-scaling
aws application-autoscaling put-scaling-policy \
  --service-namespace dynamodb \
  --resource-id table/CuratedEvents \
  --scalable-dimension dynamodb:table:WriteCapacityUnits \
  --policy-name ScaleUp \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration \
    'PredefinedMetricSpecification={PredefinedMetricType=DynamoDBWriteCapacityUtilization},TargetValue=70.0'
```

---

#### Issue: API Gateway CORS Errors

**Symptoms:**
```
Access-Control-Allow-Origin header missing
```

**Diagnosis:**
```bash
# Test OPTIONS request
curl -X OPTIONS $API_URL/ingest \
  -H "Origin: https://example.com" \
  -H "Access-Control-Request-Method: POST" -v

# Check API Gateway CORS config
aws apigateway get-method \
  --rest-api-id xyz789 \
  --resource-id abc123 \
  --http-method OPTIONS
```

**Solution:**
```bash
# Update SAM template
cat >> infrastructure/template.yaml << 'EOF'
      Cors:
        AllowOrigin: "'*'"
        AllowHeaders: "'Content-Type,X-Amz-Date,Authorization,X-Api-Key'"
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
EOF

# Redeploy
sam deploy
```

---

## Maintenance Procedures

### Daily Tasks

```bash
# Morning health check
./scripts/daily_health_check.sh

# Check Lambda error rates
for func in ingestion-lambda transformation-lambda analytics-lambda; do
  echo "=== $func ==="
  aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Errors \
    --dimensions Name=FunctionName,Value=$func \
    --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 86400 \
    --statistics Sum
done

# Check DLQ depth
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789/processing-dlq \
  --attribute-names ApproximateNumberOfMessages

# Review QuickSight dashboards
echo "Review dashboards at: https://quicksight.aws.amazon.com/"
```

### Weekly Tasks

```bash
# Review cost and usage
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=SERVICE

# Clean up old CloudWatch Logs
for log_group in $(aws logs describe-log-groups --query 'logGroups[*].logGroupName' --output text); do
  aws logs put-retention-policy \
    --log-group-name $log_group \
    --retention-in-days 30
done

# Review and optimize Lambda memory
./scripts/analyze_lambda_performance.sh

# Backup DynamoDB table
aws dynamodb create-backup \
  --table-name CuratedEvents \
  --backup-name weekly-backup-$(date +%Y%m%d)
```

### Monthly Tasks

```bash
# Review and update CloudWatch alarms
aws cloudwatch describe-alarms

# Review IAM permissions (least privilege)
./scripts/audit_iam_permissions.sh

# Update Lambda runtimes if needed
aws lambda list-functions --query 'Functions[?Runtime==`python3.8`]'

# Archive old data
python scripts/archive_old_data.py --older-than 90

# Update this runbook with lessons learned
git pull
# Review and update procedures
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective):
  - DynamoDB: 5 minutes (point-in-time recovery)
  - S3 raw events: 0 (synchronous writes)
  - Lambda code: 0 (version controlled)

- **RTO** (Recovery Time Objective):
  - Full stack: 15 minutes (CloudFormation/SAM deployment)
  - Lambda functions: 2 minutes (version rollback)
  - DynamoDB: 10 minutes (restore from backup)

### Backup Strategy

```bash
# Daily automated backups
cat > scripts/daily_backup.sh << 'EOF'
#!/bin/bash

# Backup DynamoDB
aws dynamodb create-backup \
  --table-name CuratedEvents \
  --backup-name daily-$(date +%Y%m%d)

# Enable point-in-time recovery
aws dynamodb update-continuous-backups \
  --table-name CuratedEvents \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

# Backup S3 to secondary region
aws s3 sync s3://raw-events-bucket s3://raw-events-backup-bucket

# Export CloudFormation template
aws cloudformation get-template \
  --stack-name serverless-data-pipeline-prod \
  --query 'TemplateBody' > backups/template-$(date +%Y%m%d).json

echo "Backup completed at $(date)"
EOF

chmod +x scripts/daily_backup.sh
```

### Disaster Recovery Procedures

#### Complete Stack Loss

**Recovery Steps (15-20 minutes):**
```bash
# 1. Redeploy from IaC
cd infrastructure
sam deploy \
  --stack-name serverless-data-pipeline-prod \
  --parameter-overrides Environment=production \
  --capabilities CAPABILITY_IAM

# 2. Restore DynamoDB from backup
BACKUP_ARN=$(aws dynamodb list-backups \
  --table-name CuratedEvents \
  --query 'BackupSummaries[0].BackupArn' --output text)

aws dynamodb restore-table-from-backup \
  --target-table-name CuratedEvents \
  --backup-arn $BACKUP_ARN

# 3. Verify API Gateway
API_URL=$(aws cloudformation describe-stacks \
  --stack-name serverless-data-pipeline-prod \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

curl -X POST $API_URL/ingest -d '{"test": true}'

# 4. Monitor for issues
watch -n 5 './scripts/health_check.sh'
```

---

## Quick Reference Card

### Most Common Operations

```bash
# Deploy stack
cd infrastructure && sam build && sam deploy

# Test API endpoint
curl -X POST $API_URL/ingest -d @test/sample.json

# View Lambda logs
aws logs tail /aws/lambda/ingestion-lambda --follow

# Check Step Functions executions
aws stepfunctions list-executions --state-machine-arn <arn>

# Query DynamoDB
aws dynamodb query --table-name CuratedEvents --key-condition-expression "eventType = :type"

# Check DLQ
aws sqs get-queue-attributes --queue-url <url> --attribute-names ApproximateNumberOfMessages

# Rollback Lambda
aws lambda update-alias --function-name ingestion-lambda --name prod --function-version <prev>
```

### Emergency Response

```bash
# P0: API Gateway down
sam deploy --stack-name serverless-data-pipeline-prod

# P0: Lambda failures
aws lambda update-alias --function-name ingestion-lambda --name prod --function-version <previous>

# P1: DLQ flooding
./scripts/replay_dlq.sh

# P1: DynamoDB throttling
aws dynamodb update-table --table-name CuratedEvents --billing-mode PAY_PER_REQUEST
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Data Engineering Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates
