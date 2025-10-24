# Serverless API Infrastructure

## Overview
AWS Lambda + API Gateway + DynamoDB stack delivering lightweight endpoints for integrations (webhooks, scheduled jobs). Managed via the Serverless Framework or AWS CDK.

## Architecture
- API Gateway REST API with custom domain, usage plans, and authorizers.
- Lambda functions written in Python/Node with shared layers and instrumentation.
- DynamoDB table for idempotency keys and persistent state; EventBridge for async workflows.
- CI/CD using GitHub Actions with AWS SAM validation and integration tests.

## Setup
1. Install dependencies: `npm install` (Serverless Framework) or `pip install -r requirements.txt` for SAM.
2. Configure AWS credentials via SSO or profile.
3. Deploy to dev: `sls deploy --stage dev` or `sam deploy --config-file samconfig.toml`.
4. Run local offline server: `sls offline` for testing.
5. Tests: `pytest` for functions, `postman/newman` for API contract tests.

## Security & Compliance
- Authorizers integrate with Cognito or IAM SigV4.
- Secrets stored in AWS Secrets Manager; environment variables encrypted with KMS.
- Logging via CloudWatch structured logs and X-Ray tracing.

## Operations
- Runbook includes scaling limits, DLQ handling, and throttling configuration.
- Observability dashboards built with CloudWatch Contributor Insights.
- Deployment approvals triggered via GitHub environments for staging/prod.

