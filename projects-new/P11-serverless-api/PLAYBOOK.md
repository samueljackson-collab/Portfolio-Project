# Operations Playbook

## Deployments
- **Dev**: `sam deploy --config-env dev --no-confirm-changeset` using the shared dev account.
- **Stage**: `sam deploy --config-env stage` after promoting artifacts from CodePipeline; requires WAF logging enabled.
- **Prod**: change sets must be reviewed; enable canary rollouts for new Lambda versions via `AutoPublishAlias` hooks.

## Daily operations
- Rotate API keys monthly; regenerate usage plans with `scripts/rotate_api_keys.py`.
- Review CloudWatch alarms for throttles and 5xx; scale provisioned concurrency if cold starts exceed SLA.
- Clear DLQ messages via `scripts/replay_dlq.py --source sqs_url` when EventBridge consumers fail.

## Run/validate
- `make status` to list active stacks, log groups, and associated alarms.
- `make tail` to stream structured logs for debugging payload validation errors.
