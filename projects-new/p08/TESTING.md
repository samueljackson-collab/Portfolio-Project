# P08 Testing Strategy (Serverless ETL)

## Strategy Overview
- **Unit Testing:** Isolate Lambda handler logic with mocked AWS services (moto, localstack); validate schema, transformations, error cases.
- **Integration Testing:** Deploy to dev account; trigger with sample S3 events; verify DynamoDB writes, Step Functions execution, output correctness.
- **End-to-End Testing:** Full workflow test with realistic file sizes; measure latency, cost, error handling paths.
- **Performance Testing:** Load test with concurrent executions; validate Lambda concurrency limits, DynamoDB autoscaling, Step Functions throughput.
- **Security Testing:** IAM policy validation (least privilege), encryption verification (KMS), VPC endpoint connectivity.
- **Chaos Engineering:** Inject Lambda failures, DynamoDB throttling, S3 eventual consistency delays; verify retry/DLQ behavior.
- **CI Stages:**
  - **Per-commit:** Lint (pylint, black), unit tests (pytest with moto), SAM template validation.
  - **Nightly:** Integration tests in dev account, cost report generation, security scans (Checkov).
  - **Pre-prod:** End-to-end regression suite, performance benchmarks, chaos experiments.

## Test Matrix
| ID | Category | Description | Preconditions | Steps | Expected | Tools |
|----|----------|-------------|---------------|-------|----------|-------|
| T01 | Unit/Lambda | Ingest handler writes to DynamoDB | Mocked S3/DynamoDB | Invoke ingest handler with S3 event | Metadata written with correct schema | pytest, moto |
| T02 | Unit/Lambda | Validate handler rejects invalid schema | Mocked services | Pass malformed JSON to validate handler | Returns validation error, routes to DLQ | pytest, jsonschema |
| T03 | Unit/Lambda | Transform handler applies business logic | Valid input data | Invoke transform with sample record | Output matches expected transformation (date parsing, aggregation) | pytest |
| T04 | Unit/Lambda | Output handler writes to S3 with partitioning | Mocked S3 | Invoke output handler | File written to correct partition (year=2024/month=12/day=03/) | pytest, moto |
| T05 | Integration/SF | Step Functions executes successfully | S3 raw bucket, SF deployed | Upload valid file to S3 | Step Functions completes, file in processed bucket, DynamoDB updated | AWS CLI, assertions |
| T06 | Integration/SF | Invalid file routes to DLQ | S3 raw bucket, SF deployed | Upload malformed file | Validation state fails, message in DLQ, SNS alert sent | AWS CLI, SQS assertions |
| T07 | Integration/SF | Retry logic on transient error | SF deployed, DynamoDB throttled | Inject throttling error | Step Functions retries 3 times with backoff, succeeds | AWS X-Ray, SF console |
| T08 | Integration/DDB | DynamoDB TTL expires old items | DynamoDB table with TTL enabled | Insert item with past TTL attribute | Item deleted after TTL scan | AWS CLI, DynamoDB scan |
| T09 | End-to-End | Process 1000-file batch | S3 raw bucket | Upload 1000 files concurrently | All files processed, <5min total latency, <1% error rate | Bash script, CloudWatch Insights |
| T10 | Performance | Lambda concurrency scaling | Lambda unreserved concurrency | Trigger 500 concurrent executions | All executions succeed, no throttling errors | Locust, CloudWatch metrics |
| T11 | Performance | DynamoDB autoscaling under load | DynamoDB provisioned with autoscaling | Generate 1000 writes/sec | Table scales up, no throttling | AWS CLI, CloudWatch |
| T12 | Security | IAM least privilege enforcement | Lambda execution role | Attempt S3 delete from Lambda | Action denied (role only has read/write) | pytest, boto3 |
| T13 | Security | KMS encryption for S3/DynamoDB | KMS CMK configured | Write data, inspect storage | Data encrypted with specified KMS key | AWS CLI, S3 metadata |
| T14 | Security | VPC endpoint usage (no internet routing) | Lambda in VPC with S3/DDB endpoints | Capture Lambda network traffic | No public IP communication, only VPC endpoint | VPC Flow Logs, CloudWatch |
| T15 | Chaos | Lambda random failure injection | Chaos extension deployed | Run SF workflow with 10% failure injection | Workflow retries, eventually succeeds or routes to DLQ | AWS Fault Injection Simulator |
| T16 | Chaos | S3 eventual consistency delay | S3 bucket with read-after-write simulation | Write file, immediately read from next Lambda | Read succeeds (retry logic handles delay) | moto advanced mode |
| T17 | Cost | ARM64 Lambda cost validation | ARM64 Lambda deployed | Execute 10,000 invocations | Cost < x86_64 baseline by ~20% | AWS Cost Explorer |
| T18 | Compliance | CloudTrail data event logging | CloudTrail trail configured | Perform S3 PUT/GET | Events logged with user identity, IP, timestamp | CloudTrail console |
| T19 | Monitoring | CloudWatch alarm triggers on errors | Alarm configured (threshold: 5 errors/5min) | Inject 5 validation failures | SNS alert fires, PagerDuty notified | CloudWatch, SNS |
| T20 | Regression | Schema evolution backward compatibility | New schema version deployed | Process files with old schema | Validation passes (backward compatible) | pytest, schema registry |

## Performance/Load Notes
- Baseline single-file latency: <10s end-to-end (S3 upload to processed output).
- Concurrent file limit: 500 files/min (Step Functions standard workflow max is 25,000 concurrent executions; Lambda concurrency limits tuned per function).
- DynamoDB autoscaling target: 70% read/write capacity utilization; scale-in cool-down 5 minutes.
- Cost benchmarks: <$0.10 per 1000 files processed (includes Lambda, Step Functions, S3, DynamoDB).
