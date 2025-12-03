# Testing Strategy — P10

## Checks
- **Unit:** Terraform module linting (tflint), Route 53 config sanity via policy tests.
- **Integration:** Failover drill using scripts to simulate primary outage and verify DNS shift + app health.
- **Data Integrity:** Checksum comparison for S3 replicated objects and RDS replica lag measurement.
- **Load:** Locust smoke hitting both regions to validate capacity.

## Commands
```bash
make lint
make plan-primary
make plan-secondary
make failover-drill
python tests/scripts/check_replication.py --bucket primary-bucket --replica-bucket secondary-bucket
```

## Acceptance Criteria
- DNS failover completes <120s.
- Replica lag <10s during steady state.
- No failed health checks after failback.
