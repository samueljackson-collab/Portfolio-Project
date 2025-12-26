# Runbook — P11 (API Gateway & Serverless Integration)

## Overview

Production operations runbook for the P11 Serverless API platform. This runbook covers Lambda function management, API Gateway operations, DynamoDB administration, incident response, and troubleshooting for the AWS SAM-based serverless architecture.

**System Components:**
- AWS SAM (Serverless Application Model) for Infrastructure as Code
- AWS Lambda functions (Python runtime)
- API Gateway REST API with CORS and authentication
- Amazon DynamoDB for data persistence
- AWS CloudWatch Logs and X-Ray for observability
- JWT/API Key authentication (Cognito/Auth0 integration)

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **API availability** | 99.9% | API Gateway health check success rate |
| **Lambda cold start latency** | < 1 second | CloudWatch Lambda initialization duration |
| **API response time (p95)** | < 500ms | API Gateway latency metrics |
| **Lambda error rate** | < 0.1% | Lambda invocation errors / total invocations |
| **DynamoDB read/write latency** | < 10ms (p99) | DynamoDB latency metrics |
| **Authentication success rate** | 99.5% | Successful authentications / total attempts |

---

## Dashboards & Alerts

### Dashboards

#### API Gateway Dashboard
```bash
# Check API Gateway metrics via CLI
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=serverless-api \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Check API Gateway error rates
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name 4XXError \
  --dimensions Name=ApiName,Value=serverless-api \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

#### Lambda Function Dashboard
```bash
# Check Lambda function invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=CreateItemFunction \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Check Lambda errors
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=CreateItemFunction \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Check Lambda duration
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=CreateItemFunction \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum

# List all Lambda functions in stack
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `serverless-api`)].FunctionName' --output table
```

#### DynamoDB Dashboard
```bash
# Check DynamoDB metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=items-table \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Check table status
aws dynamodb describe-table --table-name items-table --query 'Table.TableStatus'

# Check item count
aws dynamodb describe-table --table-name items-table --query 'Table.ItemCount'
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | API Gateway 5XX error rate > 5% | Immediate | Rollback deployment, check Lambda logs |
| **P0** | Lambda function out of memory | Immediate | Increase memory, investigate memory leak |
| **P1** | Lambda cold start > 3 seconds | 15 minutes | Optimize function, enable provisioned concurrency |
| **P1** | DynamoDB throttling errors | 15 minutes | Increase capacity or enable auto-scaling |
| **P1** | Authentication service down | 15 minutes | Check Cognito/Auth0 status, enable fallback |
| **P2** | Lambda error rate > 1% | 30 minutes | Review logs, investigate errors |
| **P2** | High DynamoDB read/write latency | 30 minutes | Check table capacity, investigate queries |
| **P3** | Lambda execution time increasing | 1 hour | Profile function, optimize code |

#### Alert Queries

```bash
# Check for Lambda errors in last hour
aws logs filter-log-events \
  --log-group-name /aws/lambda/CreateItemFunction \
  --start-time $(($(date +%s) - 3600))000 \
  --filter-pattern "ERROR"

# Check API Gateway access logs
aws logs tail /aws/apigateway/serverless-api/access --follow

# Check X-Ray traces for errors
aws xray get-trace-summaries \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --end-time $(date -u +%s) \
  --filter-expression 'error = true OR fault = true'
```

---

## Standard Operations

### Stack Deployment

#### Deploy to Development
```bash
# 1. Validate SAM template
aws cloudformation validate-template --template-body file://template.yaml

# 2. Build SAM application
make build

# 3. Deploy to dev environment
make deploy-dev STACK_NAME=serverless-api-dev STAGE=dev

# 4. Verify deployment
aws cloudformation describe-stacks \
  --stack-name serverless-api-dev \
  --query 'Stacks[0].StackStatus'

# 5. Get API endpoint
aws cloudformation describe-stacks \
  --stack-name serverless-api-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

#### Deploy to Production
```bash
# Production deployments require approval and change management

# 1. Build and package
make build
sam package \
  --template-file template.yaml \
  --output-template-file packaged.yaml \
  --s3-bucket deployment-artifacts-prod

# 2. Create change set
sam deploy \
  --template-file packaged.yaml \
  --stack-name serverless-api-prod \
  --parameter-overrides Stage=prod \
  --capabilities CAPABILITY_IAM \
  --no-execute-changeset

# 3. Review change set
aws cloudformation describe-change-set \
  --stack-name serverless-api-prod \
  --change-set-name <changeset-name>

# 4. Execute change set after approval
aws cloudformation execute-change-set \
  --stack-name serverless-api-prod \
  --change-set-name <changeset-name>

# 5. Monitor deployment
aws cloudformation wait stack-update-complete \
  --stack-name serverless-api-prod
```

#### Rollback Deployment
```bash
# Quick rollback to previous stack version
aws cloudformation cancel-update-stack --stack-name serverless-api-prod

# Or delete and recreate from last known good
aws cloudformation delete-stack --stack-name serverless-api-prod
# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name serverless-api-prod
# Redeploy from previous commit/tag
git checkout v1.2.0
make deploy-prod
```

### Lambda Function Management

#### Update Function Code
```bash
# Update single function without full SAM deploy
cd functions/create_item
zip -r function.zip .
aws lambda update-function-code \
  --function-name CreateItemFunction \
  --zip-file fileb://function.zip

# Wait for update to complete
aws lambda wait function-updated \
  --function-name CreateItemFunction

# Verify new code is active
aws lambda get-function --function-name CreateItemFunction \
  --query 'Configuration.LastUpdateStatus'
```

#### Invoke Function Locally
```bash
# Test function locally with SAM
sam local invoke CreateItemFunction \
  --event events/create-item.json \
  --env-vars env.json

# Start local API Gateway
sam local start-api \
  --env-vars env.json \
  --port 3000

# Test local endpoint
curl -X POST http://localhost:3000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"test","value":"123"}'
```

#### View Lambda Logs
```bash
# Tail logs in real-time
aws logs tail /aws/lambda/CreateItemFunction --follow

# View recent logs
aws logs tail /aws/lambda/CreateItemFunction --since 1h

# Filter for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/CreateItemFunction \
  --start-time $(($(date +%s) - 3600))000 \
  --filter-pattern "ERROR"

# Get last 100 log events
aws logs tail /aws/lambda/CreateItemFunction --format short | head -100
```

#### Configure Function Settings
```bash
# Update memory allocation (affects CPU allocation)
aws lambda update-function-configuration \
  --function-name CreateItemFunction \
  --memory-size 512

# Update timeout
aws lambda update-function-configuration \
  --function-name CreateItemFunction \
  --timeout 30

# Update environment variables
aws lambda update-function-configuration \
  --function-name CreateItemFunction \
  --environment 'Variables={TABLE_NAME=items-table-new,LOG_LEVEL=DEBUG}'

# Enable provisioned concurrency (eliminates cold starts)
aws lambda put-provisioned-concurrency-config \
  --function-name CreateItemFunction \
  --qualifier $LATEST \
  --provisioned-concurrent-executions 5
```

### API Gateway Operations

#### Test API Endpoints
```bash
# Get API endpoint URL
API_URL=$(aws cloudformation describe-stacks \
  --stack-name serverless-api-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

# Test health endpoint
curl -s "${API_URL}/health"

# Test CRUD operations
# Create item
curl -X POST "${API_URL}/items" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -d '{"name":"test-item","value":"123"}'

# Read item
curl -X GET "${API_URL}/items/item-id" \
  -H "Authorization: Bearer ${JWT_TOKEN}"

# Update item
curl -X PUT "${API_URL}/items/item-id" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -d '{"name":"updated-item","value":"456"}'

# Delete item
curl -X DELETE "${API_URL}/items/item-id" \
  -H "Authorization: Bearer ${JWT_TOKEN}"
```

#### Enable/Disable API Caching
```bash
# Enable caching on stage
aws apigateway update-stage \
  --rest-api-id <api-id> \
  --stage-name dev \
  --patch-operations \
    op=replace,path=/cacheClusterEnabled,value=true \
    op=replace,path=/cacheClusterSize,value=0.5

# Flush cache
aws apigateway flush-stage-cache \
  --rest-api-id <api-id> \
  --stage-name dev
```

#### Update API Throttling
```bash
# Set throttling limits
aws apigateway update-stage \
  --rest-api-id <api-id> \
  --stage-name prod \
  --patch-operations \
    op=replace,path=/throttle/rateLimit,value=1000 \
    op=replace,path=/throttle/burstLimit,value=2000
```

### DynamoDB Operations

#### Query and Scan Table
```bash
# Get item by ID
aws dynamodb get-item \
  --table-name items-table \
  --key '{"id":{"S":"item-123"}}'

# Query items (requires sort key)
aws dynamodb query \
  --table-name items-table \
  --key-condition-expression "id = :id" \
  --expression-attribute-values '{":id":{"S":"item-123"}}'

# Scan entire table (expensive!)
aws dynamodb scan \
  --table-name items-table \
  --max-items 100

# Count items
aws dynamodb scan \
  --table-name items-table \
  --select COUNT
```

#### Backup and Restore
```bash
# Create on-demand backup
aws dynamodb create-backup \
  --table-name items-table \
  --backup-name items-table-backup-$(date +%Y%m%d-%H%M%S)

# List backups
aws dynamodb list-backups --table-name items-table

# Restore from backup
aws dynamodb restore-table-from-backup \
  --target-table-name items-table-restored \
  --backup-arn <backup-arn>
```

#### Enable Point-in-Time Recovery
```bash
# Enable PITR (allows restore to any point in last 35 days)
aws dynamodb update-continuous-backups \
  --table-name items-table \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

# Restore to specific time
aws dynamodb restore-table-to-point-in-time \
  --source-table-name items-table \
  --target-table-name items-table-restored \
  --restore-date-time "2025-11-09T12:00:00Z"
```

#### Update Table Capacity
```bash
# Update provisioned capacity
aws dynamodb update-table \
  --table-name items-table \
  --provisioned-throughput ReadCapacityUnits=10,WriteCapacityUnits=5

# Enable auto-scaling
aws application-autoscaling register-scalable-target \
  --service-namespace dynamodb \
  --resource-id table/items-table \
  --scalable-dimension dynamodb:table:ReadCapacityUnits \
  --min-capacity 5 \
  --max-capacity 100

aws application-autoscaling put-scaling-policy \
  --service-namespace dynamodb \
  --resource-id table/items-table \
  --scalable-dimension dynamodb:table:ReadCapacityUnits \
  --policy-name ReadScalingPolicy \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration \
    'PredefinedMetricSpecification={PredefinedMetricType=DynamoDBReadCapacityUtilization},TargetValue=70.0'
```

---

## Incident Response

### Detection

**Automated Detection:**
- CloudWatch Alarms for Lambda errors, API Gateway 5XX errors
- X-Ray traces showing faults and errors
- DynamoDB throttling alarms

**Manual Detection:**
```bash
# Check recent Lambda errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/CreateItemFunction \
  --start-time $(($(date +%s) - 3600))000 \
  --filter-pattern "ERROR"

# Check API Gateway errors
aws logs filter-log-events \
  --log-group-name /aws/apigateway/serverless-api/access \
  --start-time $(($(date +%s) - 3600))000 \
  --filter-pattern "5XX"

# Check CloudFormation stack status
aws cloudformation describe-stacks \
  --stack-name serverless-api-prod \
  --query 'Stacks[0].StackStatus'
```

### Triage

#### Severity Classification

**P0: Complete Outage**
- API Gateway returning 5XX errors > 5%
- Lambda functions out of memory (OOM)
- DynamoDB table unavailable
- Authentication service down

**P1: Degraded Service**
- Lambda error rate > 1%
- API response time > 2 seconds (p95)
- DynamoDB throttling errors
- Cold start latency > 3 seconds

**P2: Warning State**
- Lambda execution time increasing
- DynamoDB capacity approaching limits
- Occasional authentication failures
- Minor API Gateway errors (4XX)

**P3: Informational**
- Lambda logs showing warnings
- API usage trending upward
- Cost anomalies

### Incident Response Procedures

#### P0: Lambda Functions Out of Memory

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check current memory configuration
aws lambda get-function-configuration \
  --function-name CreateItemFunction \
  --query 'MemorySize'

# 2. Check recent invocations for OOM
aws logs filter-log-events \
  --log-group-name /aws/lambda/CreateItemFunction \
  --start-time $(($(date +%s) - 3600))000 \
  --filter-pattern "Task timed out OR Memory Size"

# 3. Emergency: Increase memory immediately
aws lambda update-function-configuration \
  --function-name CreateItemFunction \
  --memory-size 1024

# 4. Verify update
aws lambda get-function-configuration \
  --function-name CreateItemFunction \
  --query 'MemorySize'
```

**Investigation (5-30 minutes):**
```bash
# Analyze memory usage patterns
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name MemoryUtilization \
  --dimensions Name=FunctionName,Value=CreateItemFunction \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum

# Check for memory leaks in logs
aws logs tail /aws/lambda/CreateItemFunction --since 24h | grep -i "memory"

# Review X-Ray traces for memory-intensive operations
aws xray get-trace-summaries \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --end-time $(date -u +%s) \
  --filter-expression 'service("CreateItemFunction")'
```

**Root Cause & Prevention:**
- Profile code to identify memory-intensive operations
- Optimize data structures and object lifecycle
- Consider breaking large functions into smaller ones
- Enable detailed CloudWatch metrics for memory tracking

---

#### P0: API Gateway 5XX Error Rate Spike

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check API Gateway errors
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name 5XXError \
  --dimensions Name=ApiName,Value=serverless-api \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Sum

# 2. Check Lambda backend errors
for func in CreateItemFunction ReadItemFunction UpdateItemFunction DeleteItemFunction; do
  echo "Checking $func..."
  aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Errors \
    --dimensions Name=FunctionName,Value=$func \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 60 \
    --statistics Sum
done

# 3. Check recent deployments
aws cloudformation describe-stack-events \
  --stack-name serverless-api-prod \
  --max-items 20

# 4. Emergency rollback if recent deployment
aws cloudformation cancel-update-stack --stack-name serverless-api-prod
```

**Investigation (5-30 minutes):**
```bash
# Check Lambda logs for errors
for func in CreateItemFunction ReadItemFunction UpdateItemFunction DeleteItemFunction; do
  echo "=== $func logs ==="
  aws logs tail /aws/lambda/$func --since 1h | grep -i "error\|exception\|traceback"
done

# Check DynamoDB for throttling
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name UserErrors \
  --dimensions Name=TableName,Value=items-table \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Sum

# Check authentication service status
# Test JWT token validation
curl -X GET "${API_URL}/items" \
  -H "Authorization: Bearer ${TEST_TOKEN}" \
  -v
```

---

#### P1: DynamoDB Throttling Errors

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check throttling metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ThrottledRequests \
  --dimensions Name=TableName,Value=items-table \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Sum

# 2. Check current capacity
aws dynamodb describe-table \
  --table-name items-table \
  --query 'Table.[ProvisionedThroughput,BillingModeSummary]'

# 3. Emergency: Increase capacity
aws dynamodb update-table \
  --table-name items-table \
  --provisioned-throughput ReadCapacityUnits=50,WriteCapacityUnits=25

# 4. Or switch to on-demand billing
aws dynamodb update-table \
  --table-name items-table \
  --billing-mode PAY_PER_REQUEST
```

**Investigation (5-30 minutes):**
```bash
# Analyze access patterns
aws logs filter-log-events \
  --log-group-name /aws/lambda/CreateItemFunction \
  --start-time $(($(date +%s) - 3600))000 \
  --filter-pattern "ThrottlingException"

# Check for hot partitions
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=items-table \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Sum,Maximum
```

**Prevention:**
- Enable auto-scaling for adaptive capacity
- Review access patterns and consider GSIs
- Implement exponential backoff in Lambda functions
- Consider DynamoDB on-demand billing for unpredictable workloads

---

#### P1: Lambda Cold Start Latency Spike

**Investigation:**
```bash
# Check initialization duration
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=CreateItemFunction \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum

# Analyze cold start vs warm start
aws logs filter-log-events \
  --log-group-name /aws/lambda/CreateItemFunction \
  --start-time $(($(date +%s) - 3600))000 \
  --filter-pattern "REPORT" | grep -i "init duration"
```

**Mitigation:**
```bash
# Option 1: Enable provisioned concurrency
aws lambda put-provisioned-concurrency-config \
  --function-name CreateItemFunction \
  --provisioned-concurrent-executions 5 \
  --qualifier $LATEST

# Option 2: Reduce package size
cd functions/create_item
# Remove unused dependencies
pip install --target ./package -r requirements.txt --upgrade
cd package && zip -r ../function.zip . && cd ..
zip -g function.zip lambda_function.py

# Option 3: Use Lambda SnapStart (for Java)
# Or implement warming strategy with EventBridge
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### Lambda Debugging
```bash
# Get function configuration
aws lambda get-function-configuration --function-name CreateItemFunction

# Get function code location
aws lambda get-function --function-name CreateItemFunction \
  --query 'Code.Location' --output text

# Test function invocation
aws lambda invoke \
  --function-name CreateItemFunction \
  --payload '{"body":"{\"name\":\"test\"}"}' \
  response.json && cat response.json

# Check concurrent executions
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name ConcurrentExecutions \
  --dimensions Name=FunctionName,Value=CreateItemFunction \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Maximum,Average
```

#### API Gateway Debugging
```bash
# Get API details
aws apigateway get-rest-apis

# Get API resources
aws apigateway get-resources --rest-api-id <api-id>

# Test API method
aws apigateway test-invoke-method \
  --rest-api-id <api-id> \
  --resource-id <resource-id> \
  --http-method POST \
  --path-with-query-string '/items' \
  --body '{"name":"test"}'

# Enable CloudWatch logging (if not enabled)
aws apigateway update-stage \
  --rest-api-id <api-id> \
  --stage-name dev \
  --patch-operations \
    op=replace,path=/accessLogSettings/destinationArn,value=arn:aws:logs:us-east-1:ACCOUNT:log-group:/aws/apigateway/serverless-api \
    op=replace,path=/accessLogSettings/format,value='$context.requestId'
```

#### DynamoDB Debugging
```bash
# Check table status and metrics
aws dynamodb describe-table --table-name items-table

# Check table streams (if enabled)
aws dynamodb describe-table \
  --table-name items-table \
  --query 'Table.StreamSpecification'

# Check GSI status
aws dynamodb describe-table \
  --table-name items-table \
  --query 'Table.GlobalSecondaryIndexes'

# Export table data (for debugging)
aws dynamodb scan --table-name items-table > table-export.json
```

### Common Issues & Solutions

#### Issue: "Lambda function execution role missing permissions"

**Symptoms:**
```bash
$ curl -X POST ${API_URL}/items
{"message": "Internal server error"}
```

**Diagnosis:**
```bash
# Check Lambda logs
aws logs tail /aws/lambda/CreateItemFunction --since 10m | grep -i "accessdenied\|unauthorized"

# Check IAM role
aws lambda get-function --function-name CreateItemFunction \
  --query 'Configuration.Role'

# Check role policies
aws iam list-attached-role-policies --role-name LambdaExecutionRole
aws iam list-role-policies --role-name LambdaExecutionRole
```

**Solution:**
```bash
# Add missing DynamoDB permissions to SAM template
# In template.yaml:
# Policies:
#   - DynamoDBCrudPolicy:
#       TableName: !Ref ItemsTable

# Redeploy stack
make deploy-dev
```

---

#### Issue: "API Gateway CORS errors"

**Symptoms:**
```
Access to fetch at 'https://api.example.com/items' from origin 'https://app.example.com'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present.
```

**Diagnosis:**
```bash
# Test OPTIONS preflight request
curl -X OPTIONS ${API_URL}/items \
  -H "Origin: https://app.example.com" \
  -H "Access-Control-Request-Method: POST" \
  -v

# Check API Gateway CORS configuration
aws apigateway get-method \
  --rest-api-id <api-id> \
  --resource-id <resource-id> \
  --http-method OPTIONS
```

**Solution:**
```bash
# Update Lambda response to include CORS headers
# In Lambda function:
# return {
#     'statusCode': 200,
#     'headers': {
#         'Access-Control-Allow-Origin': '*',
#         'Access-Control-Allow-Headers': 'Content-Type,Authorization',
#         'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
#     },
#     'body': json.dumps(response)
# }

# Or enable CORS in SAM template:
# Cors:
#   AllowOrigin: "'*'"
#   AllowHeaders: "'*'"
#   AllowMethods: "'*'"

# Redeploy
make deploy-dev
```

---

#### Issue: "DynamoDB item not found"

**Symptoms:**
```bash
$ curl -X GET ${API_URL}/items/test-id
{"message": "Item not found"}
```

**Diagnosis:**
```bash
# Check if item exists in table
aws dynamodb get-item \
  --table-name items-table \
  --key '{"id":{"S":"test-id"}}'

# Scan table for items
aws dynamodb scan --table-name items-table --max-items 10

# Check Lambda logs for query errors
aws logs tail /aws/lambda/ReadItemFunction --since 10m
```

**Solution:**
```bash
# Verify key schema matches
aws dynamodb describe-table \
  --table-name items-table \
  --query 'Table.KeySchema'

# Update Lambda function to use correct key format
# Redeploy function
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 5 minutes (DynamoDB PITR)
- **RTO** (Recovery Time Objective): 15 minutes (SAM stack recreation)

### Backup Strategy

**DynamoDB Backups:**
```bash
# Enable Point-in-Time Recovery (automated continuous backups)
aws dynamodb update-continuous-backups \
  --table-name items-table \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

# Create on-demand backup (before major changes)
aws dynamodb create-backup \
  --table-name items-table \
  --backup-name items-table-backup-$(date +%Y%m%d-%H%M%S)

# Schedule daily backups via Lambda/EventBridge
# See scripts/backup-dynamodb.py
```

**Code and Configuration Backups:**
```bash
# SAM template and Lambda code in Git
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0

# Export stack template
aws cloudformation get-template \
  --stack-name serverless-api-prod \
  --query 'TemplateBody' > backup/stack-$(date +%Y%m%d).yaml

# Export API Gateway configuration
aws apigateway get-export \
  --rest-api-id <api-id> \
  --stage-name prod \
  --export-type swagger \
  backup/api-swagger-$(date +%Y%m%d).json
```

### Disaster Recovery Procedures

#### Complete Stack Loss

**Recovery Steps (15-20 minutes):**
```bash
# 1. Verify disaster scope
aws cloudformation describe-stacks --stack-name serverless-api-prod

# 2. Check DynamoDB table status
aws dynamodb describe-table --table-name items-table

# 3. If stack deleted, redeploy from Git
git pull origin main
# Or checkout last known good version
git checkout v1.0.0

# 4. Deploy stack
make build
make deploy-prod STACK_NAME=serverless-api-prod STAGE=prod

# 5. Verify deployment
aws cloudformation describe-stacks \
  --stack-name serverless-api-prod \
  --query 'Stacks[0].StackStatus'

# 6. If DynamoDB table lost, restore from backup
aws dynamodb restore-table-from-backup \
  --target-table-name items-table \
  --backup-arn <backup-arn>

# Or restore from Point-in-Time
aws dynamodb restore-table-to-point-in-time \
  --source-table-name items-table-old \
  --target-table-name items-table \
  --restore-date-time "2025-11-09T12:00:00Z"

# 7. Test API endpoints
API_URL=$(aws cloudformation describe-stacks \
  --stack-name serverless-api-prod \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

curl -s "${API_URL}/health"
curl -X GET "${API_URL}/items" -H "Authorization: Bearer ${JWT_TOKEN}"
```

#### DynamoDB Data Loss

**Recovery Steps (5-10 minutes):**
```bash
# 1. Stop all writes to table
# Update Lambda functions to return read-only mode

# 2. Restore from Point-in-Time Recovery
aws dynamodb restore-table-to-point-in-time \
  --source-table-name items-table \
  --target-table-name items-table-restored \
  --restore-date-time "2025-11-10T08:00:00Z" \
  --use-latest-restorable-time

# 3. Wait for restore to complete
aws dynamodb describe-table --table-name items-table-restored \
  --query 'Table.TableStatus'

# 4. Update Lambda functions to use restored table
aws lambda update-function-configuration \
  --function-name CreateItemFunction \
  --environment 'Variables={TABLE_NAME=items-table-restored}'

# Repeat for all functions

# 5. Test data integrity
aws dynamodb scan --table-name items-table-restored --select COUNT

# 6. Verify application functionality
make test-api
```

### DR Drill Procedure

**Quarterly DR Drill (1 hour):**
```bash
# 1. Document current state
aws cloudformation describe-stacks --stack-name serverless-api-prod > dr-drill-before.json
aws dynamodb describe-table --table-name items-table > dr-drill-table-before.json

# 2. Announce drill in Slack #infrastructure
echo "DR drill starting at $(date)" | tee dr-drill-log.txt

# 3. Simulate disaster in non-prod environment
aws cloudformation delete-stack --stack-name serverless-api-dev
aws cloudformation wait stack-delete-complete --stack-name serverless-api-dev

# 4. Start recovery timer
START_TIME=$(date +%s)

# 5. Execute recovery
make deploy-dev STACK_NAME=serverless-api-dev STAGE=dev

# 6. Verify recovery
aws cloudformation describe-stacks --stack-name serverless-api-dev

# 7. Test API functionality
make test-api

# 8. Calculate recovery time
END_TIME=$(date +%s)
RECOVERY_TIME=$((END_TIME - START_TIME))
echo "Recovery completed in $RECOVERY_TIME seconds" | tee -a dr-drill-log.txt

# 9. Document results
echo "Target RTO: 900 seconds (15 minutes)" | tee -a dr-drill-log.txt
echo "Actual recovery time: $RECOVERY_TIME seconds" | tee -a dr-drill-log.txt

# 10. Update runbook with lessons learned
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
```bash
# Check Lambda error rates
for func in CreateItemFunction ReadItemFunction UpdateItemFunction DeleteItemFunction; do
  echo "Checking $func..."
  aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Errors \
    --dimensions Name=FunctionName,Value=$func \
    --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 3600 \
    --statistics Sum
done

# Check API Gateway health
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name 5XXError \
  --dimensions Name=ApiName,Value=serverless-api \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum

# Check DynamoDB capacity
aws dynamodb describe-table --table-name items-table \
  --query 'Table.[ProvisionedThroughput,TableStatus]'
```

#### Weekly Tasks
```bash
# Review CloudWatch Logs Insights queries
# Top errors:
aws logs start-query \
  --log-group-name /aws/lambda/CreateItemFunction \
  --start-time $(($(date +%s) - 604800)) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/ | stats count() by @message'

# Review Lambda duration trends
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=CreateItemFunction \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Average,Maximum

# Review DynamoDB usage patterns
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=items-table \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Sum,Average

# Check for unused Lambda functions
aws lambda list-functions --query 'Functions[?LastModified<`2025-01-01`].FunctionName'
```

#### Monthly Tasks
```bash
# Review and rotate IAM credentials
# Review Lambda function permissions
for func in $(aws lambda list-functions --query 'Functions[].FunctionName' --output text); do
  echo "=== $func ==="
  aws lambda get-policy --function-name $func 2>/dev/null || echo "No resource policy"
done

# Update Lambda runtimes (security patches)
# Check for deprecated runtimes
aws lambda list-functions \
  --query 'Functions[?Runtime==`python3.7` || Runtime==`python3.8`].[FunctionName,Runtime]' \
  --output table

# Create monthly DynamoDB backup
aws dynamodb create-backup \
  --table-name items-table \
  --backup-name items-table-monthly-$(date +%Y%m)

# Review and delete old backups (keep last 3 months)
aws dynamodb list-backups --table-name items-table

# Review costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --filter file://filter.json

# Update runbook documentation
```

### Upgrade Procedures

#### Update Lambda Runtime
```bash
# 1. Test new runtime locally
sam local invoke CreateItemFunction --event events/create-item.json

# 2. Update SAM template
# In template.yaml:
# Runtime: python3.11

# 3. Test in dev environment
make build
make deploy-dev

# 4. Verify functionality
make test-api

# 5. Deploy to production (during maintenance window)
make deploy-prod

# 6. Monitor for issues
aws logs tail /aws/lambda/CreateItemFunction --follow
```

#### Update Dependencies
```bash
# 1. Update requirements.txt
cd functions/create_item
pip install --upgrade boto3

# 2. Test locally
pytest tests/

# 3. Update and deploy
make build
make deploy-dev

# 4. Run integration tests
make test-api

# 5. Deploy to production
make deploy-prod
```

---

## Operational Best Practices

### Pre-Deployment Checklist
- [ ] Code reviewed and approved
- [ ] Unit tests passing (`pytest tests/`)
- [ ] SAM template validated (`aws cloudformation validate-template`)
- [ ] Tested in dev environment
- [ ] Change management ticket created (for production)
- [ ] Rollback plan documented
- [ ] Monitoring and alerts verified

### Post-Deployment Checklist
- [ ] Stack deployment completed successfully
- [ ] All Lambda functions in Active state
- [ ] API endpoints responding correctly
- [ ] DynamoDB table accessible
- [ ] CloudWatch alarms active
- [ ] X-Ray tracing working
- [ ] Monitor for 30 minutes

### Standard Change Window
- **Time:** Tuesday/Thursday, 10:00 AM - 12:00 PM ET
- **Approval:** Required for production changes
- **Blackout:** Avoid Friday deployments, holidays, peak traffic periods

### Escalation Path

| Level | Role | Response Time | Contact |
|-------|------|---------------|---------|
| L1 | On-call engineer | 15 minutes | Slack #serverless-ops |
| L2 | Team lead | 30 minutes | Direct message |
| L3 | Engineering manager | 1 hour | Phone call |

---

## Quick Reference

### Common Commands
```bash
# Check stack status
aws cloudformation describe-stacks --stack-name serverless-api-prod

# Deploy stack
make deploy-prod

# View Lambda logs
aws logs tail /aws/lambda/CreateItemFunction --follow

# Test API
curl -X GET ${API_URL}/items -H "Authorization: Bearer ${JWT_TOKEN}"

# Rollback deployment
aws cloudformation cancel-update-stack --stack-name serverless-api-prod

# Create DynamoDB backup
aws dynamodb create-backup --table-name items-table --backup-name backup-$(date +%Y%m%d)
```

### Emergency Response
```bash
# P0: Lambda OOM - Increase memory
aws lambda update-function-configuration --function-name CreateItemFunction --memory-size 1024

# P0: API Gateway errors - Rollback stack
aws cloudformation cancel-update-stack --stack-name serverless-api-prod

# P1: DynamoDB throttling - Increase capacity
aws dynamodb update-table --table-name items-table --billing-mode PAY_PER_REQUEST

# P1: Cold start issues - Enable provisioned concurrency
aws lambda put-provisioned-concurrency-config --function-name CreateItemFunction --provisioned-concurrent-executions 5
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Platform Engineering Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates

## Evidence & Verification

Verification summary: Baseline evidence captured to validate the latest quickstart configuration and document supporting artifacts for audits.

**Evidence artifacts**
- [Screenshot](./docs/evidence/screenshot.svg)
- [Run log](./docs/evidence/run-log.txt)
- [Dashboard export](./docs/evidence/dashboard-export.json)
- [Load test summary](./docs/evidence/load-test-summary.txt)

### Evidence Checklist

| Evidence Item | Location | Status |
| --- | --- | --- |
| Screenshot captured | `docs/evidence/screenshot.svg` | ✅ |
| Run log captured | `docs/evidence/run-log.txt` | ✅ |
| Dashboard export captured | `docs/evidence/dashboard-export.json` | ✅ |
| Load test summary captured | `docs/evidence/load-test-summary.txt` | ✅ |
