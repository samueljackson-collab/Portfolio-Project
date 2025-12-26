# P08 Metrics & Dashboards

## Lambda Health Dashboard

**Purpose:** Monitor Lambda function performance, errors, and cost efficiency.

**Metrics:**
- **Invocation Count** (AWS/Lambda `Invocations`): Count of Lambda executions per function (5-min granularity)
- **Error Rate** (AWS/Lambda `Errors / Invocations * 100`): Percentage of failed invocations
- **Throttles** (AWS/Lambda `Throttles`): Count of executions rejected due to concurrency limits
- **Duration** (AWS/Lambda `Duration`): p50, p95, p99 execution time in milliseconds
- **Concurrent Executions** (AWS/Lambda `ConcurrentExecutions`): Peak concurrent invocations
- **Cold Start Rate** (`InitDuration / Duration * 100`): Percentage of invocations with cold starts
- **Memory Utilization** (CloudWatch Logs Insights): Actual memory used vs allocated memory

**Widgets:**
```yaml
LambdaInvocations:
  Type: Metric
  Properties:
    Metrics:
      - [AWS/Lambda, Invocations, FunctionName, ingest-handler, {stat: Sum, period: 300}]
      - [AWS/Lambda, Invocations, FunctionName, validate-handler, {stat: Sum, period: 300}]
      - [AWS/Lambda, Invocations, FunctionName, transform-handler, {stat: Sum, period: 300}]
      - [AWS/Lambda, Invocations, FunctionName, output-handler, {stat: Sum, period: 300}]
    YAxis:
      left: {label: Invocations}
    Period: 300
    Stat: Sum
    Title: Lambda Invocations (5-min)

LambdaErrorRate:
  Type: Metric
  Properties:
    Metrics:
      - [AWS/Lambda, Errors, FunctionName, ingest-handler, {id: e1, stat: Sum, visible: false}]
      - [AWS/Lambda, Invocations, FunctionName, ingest-handler, {id: i1, stat: Sum, visible: false}]
      - [{expression: "(e1/i1)*100", label: "Ingest Error %", id: error1}]
      - [{expression: "(e2/i2)*100", label: "Validate Error %", id: error2}]
    Annotations:
      horizontal:
        - {value: 5, label: "SLA Threshold (5%)", fill: above, color: "#ff0000"}
    YAxis:
      left: {label: Error Rate %, min: 0, max: 10}
    Title: Lambda Error Rate (Target: <1%)

LambdaLatency:
  Type: Metric
  Properties:
    Metrics:
      - [AWS/Lambda, Duration, FunctionName, transform-handler, {stat: p95, period: 300}]
      - [AWS/Lambda, Duration, FunctionName, transform-handler, {stat: p99, period: 300}]
    Annotations:
      horizontal:
        - {value: 5000, label: "5s SLA", color: "#ff7f0e"}
    YAxis:
      left: {label: Milliseconds}
    Title: Transform Lambda Latency (p95/p99)

LambdaCostEfficiency:
  Type: Metric
  Properties:
    # Custom metric logged from Lambda (cost per invocation)
    Metrics:
      - [ETL/Cost, CostPerInvocation, FunctionName, transform-handler, {stat: Average}]
    YAxis:
      left: {label: USD}
    Title: Lambda Cost Per Invocation (Optimization Target: <$0.0001)
```

**Alerts:**
- **LambdaErrorRateHigh:** Error rate >5% for 2 consecutive 5-min periods → SNS → PagerDuty (P2)
- **LambdaThrottlingDetected:** Throttles >10 in 5 min → SNS → Slack #data-alerts (P3)
- **LambdaLatencyHigh:** p95 duration >5s for 10 min → SNS → Slack (P3)
- **LambdaColdStartHigh:** Cold start rate >30% → Email to team (informational, investigate optimization)

---

## Step Functions Workflow Dashboard

**Purpose:** Track Step Functions execution health, state transitions, and failure patterns.

**Metrics:**
- **Executions Started** (AWS/States `ExecutionsStarted`): Total workflow invocations
- **Executions Succeeded** (AWS/States `ExecutionsSucceeded`): Successful completions
- **Executions Failed** (AWS/States `ExecutionsFailed`): Failed workflows (includes retries exhausted)
- **Executions Timed Out** (AWS/States `ExecutionsTimedOut`): Workflows exceeding timeout
- **Executions Aborted** (AWS/States `ExecutionsAborted`): Manually stopped executions
- **Execution Time** (AWS/States `ExecutionTime`): p50, p95 workflow duration in milliseconds
- **State Transition Rate** (AWS/States `StateTransition`): Count of state changes (indicates workflow complexity)

**Widgets:**
```yaml
StepFunctionsSuccessRate:
  Type: Metric
  Properties:
    Metrics:
      - [AWS/States, ExecutionsSucceeded, StateMachineArn, "arn:aws:states:us-east-1:ACCOUNT:stateMachine:etl-workflow", {id: succeeded, stat: Sum, visible: false}]
      - [AWS/States, ExecutionsStarted, StateMachineArn, "arn:aws:states:us-east-1:ACCOUNT:stateMachine:etl-workflow", {id: started, stat: Sum, visible: false}]
      - [{expression: "(succeeded/started)*100", label: "Success Rate %", id: successrate}]
    Annotations:
      horizontal:
        - {value: 99, label: "SLA: 99%", fill: below, color: "#ff0000"}
    YAxis:
      left: {label: Success %, min: 95, max: 100}
    Title: Step Functions Success Rate (Target: >99%)

StepFunctionsFailuresByState:
  Type: Log
  Properties:
    Query: |
      SOURCE '/aws/states/etl-workflow'
      | filter type = "ExecutionFailed"
      | parse cause /\"errorType\":\"(?<errorType>[^\"]+)\"/
      | stats count() by errorType
    Title: Failures by Error Type (Last 1 Hour)

StepFunctionsExecutionDuration:
  Type: Metric
  Properties:
    Metrics:
      - [AWS/States, ExecutionTime, StateMachineArn, ARN, {stat: p50}]
      - [AWS/States, ExecutionTime, StateMachineArn, ARN, {stat: p95}]
      - [AWS/States, ExecutionTime, StateMachineArn, ARN, {stat: p99}]
    Annotations:
      horizontal:
        - {value: 30000, label: "30s SLA", color: "#d62728"}
    YAxis:
      left: {label: Milliseconds}
    Title: Workflow Execution Time (p50/p95/p99)
```

**Alerts:**
- **StepFunctionsSuccessRateLow:** Success rate <99% for 15 min → PagerDuty (P2)
- **StepFunctionsExecutionsTimedOut:** Timeouts >5 in 30 min → Slack (P3)
- **StepFunctionsExecutionsSpikeAnomalous:** Executions started >3 std dev from mean → Email (investigate event loop)

---

## End-to-End ETL Pipeline Dashboard

**Purpose:** Holistic view of data flow from S3 ingestion to output, including data quality and SLA adherence.

**Metrics:**
- **Files Ingested** (Custom CloudWatch metric from ingest Lambda): Count of S3 events processed
- **Files Processed Successfully** (Custom metric from output Lambda): Count of files written to processed bucket
- **Files Routed to DLQ** (SQS `ApproximateNumberOfMessagesVisible`): Count of validation failures
- **Data Volume Processed** (Custom metric): GB of data transformed (sum of file sizes)
- **End-to-End Latency** (Custom metric): Time from S3 upload to processed output (p95)
- **DynamoDB Write Throughput** (AWS/DynamoDB `ConsumedWriteCapacityUnits`): Metadata table usage
- **S3 Request Count** (AWS/S3 `AllRequests`): GET/PUT operations on raw/processed buckets
- **Cost Per File** (Calculated metric): Total pipeline cost / files processed

**Widgets:**
```yaml
FileThroughput:
  Type: Metric
  Properties:
    Metrics:
      - [ETL/Pipeline, FilesIngested, {stat: Sum, period: 300, label: "Ingested"}]
      - [ETL/Pipeline, FilesProcessedSuccess, {stat: Sum, period: 300, label: "Processed"}]
      - [ETL/Pipeline, FilesRoutedToDLQ, {stat: Sum, period: 300, label: "DLQ"}]
    YAxis:
      left: {label: File Count}
    Title: File Throughput (5-min intervals)

DataQualityRate:
  Type: Metric
  Properties:
    Metrics:
      - [{expression: "(processed/(ingested))*100", label: "Quality %", id: quality}]
      - [ETL/Pipeline, FilesProcessedSuccess, {id: processed, visible: false}]
      - [ETL/Pipeline, FilesIngested, {id: ingested, visible: false}]
    Annotations:
      horizontal:
        - {value: 95, label: "Min Acceptable (95%)", fill: below, color: "#ff0000"}
    YAxis:
      left: {label: Quality %, min: 90, max: 100}
    Title: Data Quality Rate (Target: >98%)

EndToEndLatency:
  Type: Log
  Properties:
    Query: |
      SOURCE '/aws/lambda/output-handler'
      | filter message like /processing_time_ms/
      | parse message /processing_time_ms=(?<latency>\d+)/
      | stats avg(latency) as AvgLatency, pct(latency, 95) as P95Latency by bin(5m)
    Title: End-to-End Latency (Upload to Output) - p95

CostPerFile:
  Type: Metric
  Properties:
    # Calculated from Cost Explorer API + file count metric
    Metrics:
      - [ETL/Cost, TotalDailyCost, {stat: Sum, label: "Daily Cost USD"}]
      - [ETL/Pipeline, FilesProcessedSuccess, {stat: Sum, id: files, visible: false}]
      - [{expression: "m1/files", label: "Cost Per File", id: costperfile}]
    YAxis:
      left: {label: USD}
    Title: Cost Efficiency (Target: <$0.10 per 1000 files)
```

**Alerts:**
- **DataQualityRateLow:** Quality rate <95% for 30 min → PagerDuty (P2) - data issue
- **EndToEndLatencyHigh:** p95 latency >60s for 20 min → Slack (P3) - performance degradation
- **DLQDepthHigh:** DLQ messages >50 → Email + Jira ticket (manual review needed)
- **CostPerFileAnomalous:** Cost per file >2x baseline → FinOps alert (investigate waste)

---

## CloudWatch Logs Insights Queries

**Lambda Memory Optimization:**
```sql
SOURCE '/aws/lambda/transform-handler'
| filter type = "REPORT"
| parse @message /Max Memory Used: (?<MaxMemoryUsed>\d+) MB/
| parse @message /Memory Size: (?<MemorySize>\d+) MB/
| stats avg(MaxMemoryUsed) as AvgMemoryUsed, max(MaxMemoryUsed) as PeakMemoryUsed, avg(MemorySize) as AllocatedMemory
| fields AvgMemoryUsed, PeakMemoryUsed, AllocatedMemory
```
**Usage:** If PeakMemoryUsed < 60% of AllocatedMemory, reduce memory allocation to save cost.

**Error Pattern Analysis:**
```sql
SOURCE '/aws/lambda/validate-handler'
| filter level = "ERROR"
| parse message /errorType=(?<errorType>[^,]+), errorMessage=(?<errorMessage>[^,]+)/
| stats count() as ErrorCount by errorType, errorMessage
| sort ErrorCount desc
| limit 10
```
**Usage:** Identify most common validation errors; prioritize schema updates or upstream data quality fixes.

**Execution Timeline (Forensics):**
```sql
SOURCE '/aws/states/etl-workflow'
| filter type = "ExecutionStarted" or type = "LambdaFunctionStarted" or type = "LambdaFunctionSucceeded" or type = "LambdaFunctionFailed" or type = "ExecutionSucceeded" or type = "ExecutionFailed"
| sort @timestamp asc
| fields @timestamp, type, details.name, details.output, details.cause
```
**Usage:** Debug stuck or failed Step Functions executions; trace state transitions.

---

## Alarm Summary

| Alarm Name | Metric | Threshold | Action |
|------------|--------|-----------|--------|
| LambdaErrorRateHigh | Errors/Invocations | >5% for 10 min | PagerDuty P2 |
| LambdaThrottlingDetected | Throttles | >10 in 5 min | Slack #data-alerts |
| StepFunctionsSuccessRateLow | ExecutionsSucceeded/ExecutionsStarted | <99% for 15 min | PagerDuty P2 |
| DLQDepthHigh | SQS ApproximateNumberOfMessagesVisible | >50 | Email + Jira ticket |
| DataQualityRateLow | FilesProcessedSuccess/FilesIngested | <95% for 30 min | PagerDuty P2 |
| CostBudgetExceeded | Monthly spend | >80% of budget | Email to FinOps + Manager |
| DynamoDBThrottlingDetected | ThrottledRequests | >0 for 10 min | Slack #data-alerts |
| S3EventLoopDetected | ExecutionsStarted | >500 in 1 min | PagerDuty P1 + Auto-disable EventBridge rule |

---

## Grafana Integration (Optional)

For teams using Grafana, export CloudWatch metrics via CloudWatch data source:

**Dashboard JSON Template:**
```json
{
  "dashboard": {
    "title": "ETL Pipeline Monitoring",
    "panels": [
      {
        "title": "Lambda Invocations",
        "targets": [
          {
            "datasource": "CloudWatch",
            "namespace": "AWS/Lambda",
            "metricName": "Invocations",
            "dimensions": {"FunctionName": "ingest-handler"},
            "statistic": "Sum",
            "period": "300"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

**Benefits of Grafana:**
- Unified dashboard for AWS + external metrics (e.g., upstream system health)
- Advanced alerting with Grafana Alerting or Prometheus Alertmanager
- Custom annotations for deployments, incidents
