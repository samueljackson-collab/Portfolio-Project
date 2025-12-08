# Architecture

The API Gateway exposes REST resources mapped to Lambda integrations. Each handler writes to DynamoDB with optimistic concurrency and emits structured logs to CloudWatch. X-Ray traces wrap inbound requests, DynamoDB calls, and third-party notifications. IAM roles enforce least privilege with per-stage API keys and usage plans.

## Flow
1. Client calls `POST /items` on API Gateway.
2. Gateway authorizer validates JWT via Amazon Cognito and forwards claims.
3. Lambda handler validates payload, writes to DynamoDB with conditional expressions, and publishes audit events to EventBridge.
4. CloudWatch Logs capture request IDs; X-Ray records subsegment timings for cold start detection.

## Dependencies
- AWS SAM CLI for packaging/deployment.
- Python 3.11 runtime with `boto3`, `pydantic`, and `aws-lambda-powertools`.
- DynamoDB table for persistence; optional EventBridge bus for async fan-out.
- VPC endpoints for DynamoDB/X-Ray in private deployments.
