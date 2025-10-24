# Cost Analysis & Optimisation Plan

The stack targets a production-grade posture while staying within a ~$190/month operating envelope in `us-east-1`. Costs assume two t3.micro application nodes running most of the month with headroom for scaling during peak events.

## Baseline Monthly Estimate
| Component | Configuration | Approx. Cost |
|-----------|---------------|--------------|
| Application Auto Scaling Group | 2× t3.micro baseline, scaling to 6 | $33 |
| Application Load Balancer | 730h + 10 LCUs | $21 |
| NAT Gateways | 2× (one per AZ) | $65 |
| RDS PostgreSQL | db.t3.micro Multi-AZ + 20 GB gp3 | $50 |
| RDS Backups | 7-day automated, 30/90-day AWS Backup | $5 |
| CloudWatch Logs & Alarms | Metrics, flow logs, dashboards | $10 |
| CloudTrail | S3 storage + API calls | $4 |
| Data Transfer | 100 GB egress | $6 |
| **Total** |  | **≈ $194 / month** |

> NAT Gateway spend dominates the envelope but preserves high availability. Removing one NAT cuts costs in half but introduces a single point of failure for outbound traffic.

## Quick Wins (Implement Immediately)
1. **Enable 1-year Reserved Instances / Savings Plans** for the two steady t3.micro application nodes and the db.t3.micro database (~30% savings → ~$20/month).
2. **Adopt Graviton (t4g.micro) instances** if the workload is ARM compatible (~20% cheaper for both EC2 and RDS).
3. **Tune CloudWatch Logs retention** – reduce flow log retention to 14 days for dev/stage environments, saving a few dollars per environment.

## Medium-Term Optimisations
1. **Compute Savings Plan (3-year)** covering 4 vCPU / 16 GB baseline brings the ASG cost under $20/month.
2. **RDS Reserved Instance (3-year standard)** – ~60% discount, reducing Multi-AZ PostgreSQL to ~$20/month.
3. **S3 Intelligent-Tiering for CloudTrail logs** – automatically moves logs older than 90 days to cheaper storage without operational work.

## Strategic Improvements
1. **Introduce AWS WAF + CloudFront** only when traffic justifies the spend (offset by reduced ALB LCUs and origin bandwidth).
2. **Evaluate NAT Instance replacement** – for development or non-critical environments, a t3.nano NAT instance + Auto Scaling health checks can drop egress cost by >$50/month (accepting manual failover risk).
3. **Leverage Spot Instances for burst capacity** – configure a mixed instance policy in the Auto Scaling group to use Spot for overflow nodes, reducing scale-out cost by up to 70% while keeping two On-Demand instances as baseline.

## Observability of Spend
- **AWS Cost Explorer** – Tag filter (`Project=aws-multi-tier`) to monitor monthly trend.
- **`aws ce get-cost-and-usage`** – Automate weekly spend reports; include in the `scripts/` directory if extended cost automation is added.
- **AWS Budgets** – Set a 80% forecast alert for the monthly goal and route notifications through the existing SNS topic.

The combination of right-sizing, reservation commitments, and intelligent tiering keeps the stack within a small-team SaaS budget while maintaining enterprise reliability characteristics.
