# Threat Model

## Assets
- Customer data stored in DynamoDB tables.
- API Gateway endpoints and JWT auth tokens.
- Lambda environment variables containing secrets and telemetry configs.

## Threats
- Unauthorized access via misconfigured authorizer or public stages.
- Injection through request bodies leading to DynamoDB expression abuse.
- Data exfiltration through verbose logs or overly permissive IAM roles.
- Denial of wallet via excessive invocations causing throttling/cost spikes.

## Mitigations
- Cognito/JWT authorizer with per-stage API keys and WAF rules against common exploits.
- Payload validation using `pydantic` schemas and request size limits enforced at API Gateway.
- IAM policies limited to table-level actions; Lambda environment secrets pulled from Secrets Manager.
- CloudWatch alarms on 4xx/5xx/Throttle metrics plus budget alerts tied to usage plans.
