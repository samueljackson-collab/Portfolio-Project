# Cost Analysis

This document provides a representative cost breakdown for the sample AWS infrastructure used throughout the guide. Adjust the values based on your workload's actual size, regions, and usage patterns.

## Baseline Monthly Estimate (us-west-2)

| Service | Configuration | Est. Monthly Cost |
|---------|---------------|-------------------|
| EC2 Auto Scaling Group | Two `t3.medium` on-demand instances | $60 |
| Application Load Balancer | 730 hours + 100 GB processed | $25 |
| RDS PostgreSQL | `db.t3.small` Multi-AZ | $50 |
| CloudFront | 100 GB data transfer out | $10 |
| Data Transfer | 500 GB cross-AZ | $45 |
| **Total** |  | **~$190** |

## Cost Optimization Ideas

- Use EC2 Auto Scaling to reduce instance counts during off-peak periods.
- Evaluate Reserved Instances or Savings Plans once workloads stabilize.
- Deploy a staging environment with smaller instance types to limit spend during development.
- Enable S3 lifecycle policies for any logging or artifact buckets.
- Periodically run AWS Cost Explorer or `infracost` to track drift.

## Tracking Costs in GitHub

- Document assumptions in pull requests when infrastructure changes might increase spend.
- Update this file whenever new components are added or existing services are resized.
- Consider adding an `infracost` GitHub Action to display delta estimates directly on pull requests.
