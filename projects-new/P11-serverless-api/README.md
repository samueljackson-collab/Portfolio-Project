# P11 – API Gateway & Serverless Backend

This service fronts a Lambda-based backend with Amazon API Gateway, DynamoDB persistence, and CloudWatch/X-Ray tracing hooks. The goal is to provide a low-latency CRUD API with IAM-scoped access while keeping cold starts minimal. Use the SAM template to deploy a dev stack, run load tests, and validate logs/traces end-to-end.

## Quick start
1. Install deps: `pip install -r requirements.txt && npm install -g aws-sam-cli`.
2. Bootstrap env: copy `.env.example` to `.env` and set `AWS_PROFILE`, `AWS_REGION`, and `DDB_TABLE`.
3. Deploy dev stack: `sam deploy --config-env dev --guided`.
4. Exercise the API: `python scripts/smoke_tests.py --stage dev`.
5. Review observability: open CloudWatch dashboards and X-Ray traces under the generated stack name.

## Key components
- `template.yaml`: API Gateway, Lambda handlers, DynamoDB table, and X-Ray sampling rules.
- `src/handlers/`: Python handlers with structured logging and idempotent writes.
- `scripts/load_test.py`: k6 wrapper for burst and sustained traffic profiles.
- `docs/runbooks.md`: incident procedures for 5xx spikes or throttle events.
