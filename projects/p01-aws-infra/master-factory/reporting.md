# Reporting

## KPIs
- ALB 5xx error rate < 1% per 5 minutes.
- RDS average latency < 20 ms.
- DR drill RTO ≤ 30 minutes; RPO ≤ 5 minutes.
- IaC drift: zero unmanaged resources per weekly drift check.

## Dashboard Outputs
- CloudWatch: ALB/RDS metrics, Route53 health, Config compliance.
- Grafana (if connected): RDS performance insights, application latency.

## Evidence Package
- Include Terraform plan/apply logs, `dr-drill.sh` JSON metrics, Config/GuardDuty status reports, and alarm screenshots.
- Store quarterly in `reports/p01/<year>-Q<qtr>/`.

## Executive Rollup
- Monthly summary of uptime, cost deltas, and completed drills.
- Highlight security scan findings and remediation closure dates.
