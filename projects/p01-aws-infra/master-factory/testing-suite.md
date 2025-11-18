# Testing Suite

## Unit Tests
- Terraform: `terraform validate`, `tflint`, and `checkov` on modules.
- Shell scripts: `shellcheck scripts/*.sh` focusing on `dr-drill.sh`.

## Integration Tests
- `pytest tests/integration/test_rds_connectivity.py` to verify RDS connectivity from app instances via bastion.
- `pytest tests/integration/test_route53_failover.py` to confirm health check failover toggles.
- `pytest tests/integration/test_config_guardduty.py` to validate AWS Config and GuardDuty detectors are enabled.

## Disaster Recovery Drills
- Execute `scripts/dr-drill.sh --region <primary> --failover-region <secondary>`.
- Validate RPO/RTO targets: RPO ≤ 5 minutes, RTO ≤ 30 minutes.
- Capture CloudWatch metrics and Route53 health check outputs as artifacts.

## CI Pipeline Gates
- Pre-merge: `make lint` -> `make test` -> `make plan` (Terraform plan).
- Release: `make apply` gated on manual approval + security scan pass.

## Evidence Collection
- Store test outputs in `artifacts/<date>/` with JSON summaries for Config, GuardDuty, and DR drills.
- Attach screenshots/logs to pull requests for audit readiness.
