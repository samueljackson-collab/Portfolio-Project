# Runbooks

## Runbook: Lambda Throttling (Error Rate Spike)

**Symptoms:**
- CloudWatch alarm: `LambdaThrottlingAlarm` in ALARM state
- Step Functions executions showing `Lambda.TooManyRequestsException` errors
- Error logs: `Rate exceeded` or `Concurrent execution limit reached`

**Impact:** Step Functions workflows failing or delayed; data processing SLA breach

**Diagnosis:**
```bash
# Check Lambda concurrent executions (current vs limit)
aws lambda get-function-concurrency --function-name ingest-handler
aws lambda get-account-settings | jq '.AccountLimit.ConcurrentExecutions'

# Query throttled invocations in last hour
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Throttles \
  --dimensions Name=FunctionName,Value=ingest-handler \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --end-time $(date -u +%s) \
  --period 300 \
  --statistics Sum

# Identify concurrent execution pattern
aws logs insights query \
  --log-group-name /aws/lambda/ingest-handler \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --end-time $(date -u +%s) \
  --query-string 'stats count() by bin(5m)'
```

**Resolution:**
1. **Immediate (stop the bleeding):**
   ```bash
   # Increase reserved concurrency for affected function
   aws lambda put-function-concurrency \
     --function-name ingest-handler \
     --reserved-concurrent-executions 200  # was 100

   # If account-level limit hit, request increase via Support
   # Support ticket: "Request concurrency limit increase from 1000 to 2000"
   ```

2. **Short-term (prevent recurrence):**
   - Implement SQS queue in front of Step Functions to buffer spikes
   - Add exponential backoff in upstream S3 event triggers
   - Review function duration (optimize to reduce concurrency needs)

3. **Long-term (architectural fix):**
   - Migrate to Step Functions Express Workflows (higher throughput)
   - Batch small files before processing (reduce invocation count)
   - Implement reserved concurrency per function based on traffic patterns

**Verification:**
```bash
# Confirm throttling stopped
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Throttles \
  --dimensions Name=FunctionName,Value=ingest-handler \
  --start-time $(date -u -d '10 minutes ago' +%s) \
  --end-time $(date -u +%s) \
  --period 60 \
  --statistics Sum
# Expected: Sum = 0 for last 10 minutes
```

---

## Runbook: Step Functions Execution Stuck (Timeout)

**Symptoms:**
- Step Functions execution status: `RUNNING` for >1 hour (expected <5 min)
- No progress on state transitions
- CloudWatch Logs show last activity >30 minutes ago

**Impact:** Files not processed; downstream consumers missing data; potential cost accumulation

**Diagnosis:**
```bash
# List long-running executions
aws stepfunctions list-executions \
  --state-machine-arn arn:aws:states:us-east-1:ACCOUNT_ID:stateMachine:etl-workflow \
  --status-filter RUNNING \
  --query 'executions[?startDate < `2024-12-03T10:00:00`]'

# Get execution history for stuck workflow
aws stepfunctions get-execution-history \
  --execution-arn arn:aws:states:us-east-1:ACCOUNT_ID:execution:etl-workflow:EXECUTION_ID \
  --reverse-order \
  --max-results 10

# Check Lambda function logs for last state
LAMBDA_ARN=$(aws stepfunctions describe-execution \
  --execution-arn EXECUTION_ARN \
  --query 'mapRunArn' --output text)
aws logs tail /aws/lambda/transform-handler --since 1h --filter-pattern ERROR
```

**Root Causes:**
- Lambda function hung (infinite loop, deadlock)
- DynamoDB/S3 API call timeout (no retry configured)
- Resource exhaustion (Lambda out of memory, killed mid-execution)

**Resolution:**
1. **Stop stuck execution:**
   ```bash
   aws stepfunctions stop-execution \
     --execution-arn arn:aws:states:us-east-1:ACCOUNT_ID:execution:etl-workflow:EXECUTION_ID \
     --cause "Manual intervention: execution timeout"
   ```

2. **Investigate root cause:**
   - Check Lambda CloudWatch Logs for errors/timeouts
   - Review X-Ray traces for slow API calls
   - Verify DynamoDB/S3 service health (AWS Health Dashboard)

3. **Fix and reprocess:**
   ```bash
   # Identify source file from execution input
   aws stepfunctions describe-execution \
     --execution-arn EXECUTION_ARN \
     --query 'input' | jq -r '.detail.object.key'

   # Re-trigger Step Functions with same input (manual)
   aws stepfunctions start-execution \
     --state-machine-arn arn:aws:states:us-east-1:ACCOUNT_ID:stateMachine:etl-workflow \
     --input file://execution-input.json \
     --name retry-$(date +%s)
   ```

4. **Preventative measures:**
   - Add Lambda timeout (e.g., 5 minutes) and Step Functions timeout (10 minutes)
   - Implement heartbeat mechanism for long-running tasks
   - Add CloudWatch alarm for executions in RUNNING state >15 minutes

**Verification:**
- New execution completes successfully
- File appears in processed bucket
- DynamoDB metadata updated

---

## Runbook: S3 Event Loop (Infinite Triggering)

**Symptoms:**
- Exponential growth in Step Functions executions (hundreds/thousands per second)
- CloudWatch alarm: Execution count spike
- S3 costs increasing rapidly (PutObject requests)
- EventBridge showing repeated events for same object key

**Impact:** Service outage due to resource exhaustion; runaway AWS costs; potential account throttling

**Diagnosis:**
```bash
# Check execution count (should be <100/min normally)
aws cloudwatch get-metric-statistics \
  --namespace AWS/States \
  --metric-name ExecutionsStarted \
  --dimensions Name=StateMachineArn,Value=STATE_MACHINE_ARN \
  --start-time $(date -u -d '10 minutes ago' +%s) \
  --end-time $(date -u +%s) \
  --period 60 \
  --statistics Sum

# Identify looping object keys
aws logs insights query \
  --log-group-name /aws/events/etl-s3-events \
  --query-string 'fields @timestamp, detail.object.key | sort @timestamp desc | limit 100'

# Check if processed bucket triggering raw bucket events (loop condition)
aws s3api get-bucket-notification-configuration --bucket processed-data-bucket
```

**Root Cause:** Lambda/Step Functions writing output to S3 bucket that triggers the same EventBridge rule (circular dependency)

**Resolution:**
1. **IMMEDIATE - Stop the loop:**
   ```bash
   # Disable EventBridge rule (breaks event chain)
   aws events disable-rule --name etl-s3-events

   # Wait 5 minutes for in-flight executions to complete
   sleep 300

   # Stop all running executions
   for exec_arn in $(aws stepfunctions list-executions \
     --state-machine-arn STATE_MACHINE_ARN \
     --status-filter RUNNING \
     --query 'executions[].executionArn' --output text); do
     aws stepfunctions stop-execution --execution-arn $exec_arn --cause "Event loop mitigation"
   done
   ```

2. **Fix event pattern to exclude processed bucket:**
   ```json
   {
     "source": ["aws.s3"],
     "detail-type": ["Object Created"],
     "detail": {
       "bucket": {
         "name": ["raw-data-bucket"]  // ONLY raw bucket, NOT processed-data-bucket
       }
     }
   }
   ```

3. **Add safeguards:**
   ```bash
   # Add S3 bucket prefix filter to EventBridge rule
   # Only trigger on raw-data-bucket objects with prefix "incoming/"
   # Ensure output Lambda writes to "processed/" prefix or different bucket

   # Update EventBridge rule with corrected pattern
   aws events put-rule \
     --name etl-s3-events \
     --event-pattern file://event-pattern-fixed.json

   # Re-enable rule
   aws events enable-rule --name etl-s3-events
   ```

4. **Monitor for recurrence:**
   ```bash
   # Set up CloudWatch alarm for execution rate >200/min
   aws cloudwatch put-metric-alarm \
     --alarm-name etl-execution-rate-spike \
     --metric-name ExecutionsStarted \
     --namespace AWS/States \
     --statistic Sum \
     --period 60 \
     --threshold 200 \
     --comparison-operator GreaterThanThreshold \
     --evaluation-periods 2
   ```

**Verification:**
- Execution rate returns to normal (<100/min)
- No new executions triggered from processed bucket
- Cost Explorer shows declining API request trend

---

## Runbook: Cost Spike (Budget Alert)

**Symptoms:**
- AWS Budgets alert: "ETL Pipeline exceeds 80% of monthly budget"
- Unexpected charges for Lambda, Step Functions, or DynamoDB
- Cost Explorer showing anomaly detection alert

**Impact:** Budget overrun; potential service suspension if account limits reached

**Diagnosis:**
```bash
# Identify top cost contributors in last 7 days
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d '7 days ago' +%F),End=$(date -u +%F) \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=SERVICE

# Drill down into Lambda costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d '7 days ago' +%F),End=$(date -u +%F) \
  --granularity DAILY \
  --metrics BlendedCost \
  --filter file://filter-lambda.json \
  --group-by Type=TAG,Key=Function

# Check for Lambda memory over-provisioning
aws lambda list-functions | jq -r '.Functions[] | "\(.FunctionName),\(.MemorySize)"'

# Review DynamoDB on-demand vs provisioned cost
aws dynamodb describe-table --table-name etl-metadata | jq '.Table.BillingModeSummary'
```

**Common Causes:**
- Lambda memory over-allocated (paying for unused memory)
- DynamoDB provisioned capacity under-utilized
- S3 storage class not optimized (Standard instead of Intelligent Tiering)
- Excessive CloudWatch Logs retention (storing GB of debug logs)
- Event loop or runaway executions

**Resolution:**
1. **Immediate cost containment:**
   ```bash
   # Reduce Lambda memory allocations (if over-provisioned)
   aws lambda update-function-configuration \
     --function-name transform-handler \
     --memory-size 512  # down from 1024

   # Switch DynamoDB to on-demand if provisioned capacity wasted
   aws dynamodb update-table \
     --table-name etl-metadata \
     --billing-mode PAY_PER_REQUEST

   # Enable S3 Intelligent Tiering for processed bucket
   aws s3api put-bucket-intelligent-tiering-configuration \
     --bucket processed-data-bucket \
     --id DailyTransition \
     --intelligent-tiering-configuration file://tiering-config.json
   ```

2. **Reduce log retention:**
   ```bash
   # Set CloudWatch Logs retention to 7 days (was 30)
   for log_group in $(aws logs describe-log-groups --query 'logGroups[].logGroupName' --output text); do
     aws logs put-retention-policy --log-group-name $log_group --retention-in-days 7
   done
   ```

3. **Monitor for sustained reduction:**
   - Check Cost Explorer daily for 7 days
   - Verify cost per processed file decreases
   - Update budget forecast based on new baseline

**Verification:**
- Cost trend in Cost Explorer shows decline
- Budget alert clears (spend <80% of monthly allocation)
- Performance SLAs still met after optimization

---

## Runbook: IAM Permission Errors (Access Denied)

**Symptoms:**
- Lambda function logs: `AccessDenied` or `User: arn:aws:sts::ACCOUNT_ID:assumed-role/lambda-execution-role is not authorized to perform: s3:PutObject`
- Step Functions executions failing at Lambda invocation
- DynamoDB errors: `User is not authorized to perform: dynamodb:PutItem`

**Impact:** Data processing halted; files stuck in raw bucket; SLA breach

**Diagnosis:**
```bash
# Review Lambda execution role policies
ROLE_NAME=$(aws lambda get-function --function-name ingest-handler \
  --query 'Configuration.Role' --output text | awk -F'/' '{print $NF}')

aws iam list-attached-role-policies --role-name $ROLE_NAME
aws iam list-role-policies --role-name $ROLE_NAME

# Get specific policy document
POLICY_ARN=$(aws iam list-attached-role-policies --role-name $ROLE_NAME \
  --query 'AttachedPolicies[0].PolicyArn' --output text)
aws iam get-policy-version \
  --policy-arn $POLICY_ARN \
  --version-id $(aws iam get-policy --policy-arn $POLICY_ARN \
    --query 'Policy.DefaultVersionId' --output text)

# Check CloudTrail for denied API calls (last 1 hour)
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=PutObject \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --query 'Events[?errorCode==`AccessDenied`]'
```

**Root Causes:**
- IAM policy too restrictive (missing required permissions)
- S3 bucket policy denying Lambda role
- KMS key policy not granting decrypt/encrypt permissions
- Resource-based policy conflict

**Resolution:**
1. **Identify missing permission from error message:**
   ```
   Example error: "is not authorized to perform: s3:PutObject on resource: arn:aws:s3:::processed-data-bucket/*"
   Missing action: s3:PutObject
   Missing resource: processed-data-bucket/*
   ```

2. **Update IAM policy:**
   ```bash
   # Add missing permission to inline policy
   aws iam put-role-policy \
     --role-name lambda-execution-role \
     --policy-name LambdaS3Access \
     --policy-document file://updated-policy.json
   ```

   Example `updated-policy.json`:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": ["s3:GetObject", "s3:PutObject"],
         "Resource": "arn:aws:s3:::processed-data-bucket/*"
       }
     ]
   }
   ```

3. **If S3 bucket policy issue, update bucket policy:**
   ```bash
   aws s3api get-bucket-policy --bucket processed-data-bucket
   # Review for Deny statements or missing Allow for Lambda role
   # Update via S3 console or CLI put-bucket-policy
   ```

4. **If KMS key policy issue:**
   ```bash
   # Grant Lambda role decrypt/encrypt permissions on KMS key
   aws kms put-key-policy \
     --key-id KEY_ID \
     --policy-name default \
     --policy file://kms-policy-updated.json
   ```

**Verification:**
```bash
# Retry failed Step Functions execution
aws stepfunctions start-execution \
  --state-machine-arn STATE_MACHINE_ARN \
  --input file://test-input.json

# Check logs for successful S3/DynamoDB operations
aws logs tail /aws/lambda/ingest-handler --since 5m --filter-pattern "Successfully"
```

**Preventative Measures:**
- Use IAM Access Analyzer to validate policies before deployment
- Implement least privilege via SAM policy templates
- Add integration tests that verify IAM permissions in CI/CD
