# Cost Optimization

## Networking
- Toggle `single_nat_gateway` to true in dev/staging to save ~$65/mo per unused AZ.
- Enable S3/DynamoDB gateway endpoints to avoid NAT data transfer.
- Adjust VPC Flow Logs retention; export to S3 if longer retention required.

## Compute
- Right-size ASG instance type using CloudWatch metrics; consider Graviton (`t4g`, `m6g`).
- Use Spot instances for stateless workloads (future enhancement via mixed instances policy).
- Enforce `desired_capacity` minimums per environment to avoid idle nodes.

## Database
- Scale storage automatically with `max_allocated_storage` instead of over-provisioning.
- Evaluate Aurora Serverless v2 for variable workloads.
- Turn on storage auto-scaling alerts.

## Storage
- Lifecycle rules transition artifacts to Glacier after 30 days and delete after 1 year.
- Clean plan files/cost reports older than 90 days.

## Tooling
- Run `scripts/cost-estimate.sh <env>` on each PR to trend deltas.
- Export Infracost JSON to the portfolio metrics dashboard.
