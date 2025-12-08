# Runbooks

## 5xx or throttle spike
1. Run `make status` to confirm API Gateway/Lambda throttle metrics.
2. Enable `provisionedConcurrency` for the hottest function via `sam sync --stack-name <stack> --resource <fn>`.
3. Inspect CloudWatch Logs filter `?ERROR ?ValidationError` to isolate failing requests.
4. If throttles persist, raise usage plan limits and increase reserved concurrency temporarily.

## DynamoDB write failures
1. Check CloudWatch metric `ConditionalCheckFailedRequests`; validate partition key distribution with `scripts/inspect_keys.py`.
2. If partitions are hot, apply key hashing and run `sam deploy` to migrate without downtime using GSIs.
3. Replay failed events from DLQ with `scripts/replay_dlq.py --stage <env>` and monitor for duplicates.

## Lost tracing
1. Confirm X-Ray daemon rights within Lambda execution role.
2. Re-run `./scripts/verify_tracing.sh` after deploying new version.
3. If traces still missing, lower sampling rate only after root cause analysis; capture evidence in `docs/incidents/*.md`.
