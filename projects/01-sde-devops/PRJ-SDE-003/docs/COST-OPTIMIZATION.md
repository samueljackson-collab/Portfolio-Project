# Cost Optimization

- Toggle `enable_nat_gateway` and `enable_nat_gateway_per_az` per environment to balance availability and spend.
- Prefer VPC endpoints for S3/DynamoDB to avoid NAT data processing charges.
- Right-size instance types and autoscaling minimums based on load testing results.
- Use CloudWatch Metrics and Cost Explorer to tag and attribute spend by environment and application component.
