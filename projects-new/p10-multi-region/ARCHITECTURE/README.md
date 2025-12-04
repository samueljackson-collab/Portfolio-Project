# Architecture

## Diagram
```
[Users]
  |
[Route 53 Failover Record]
  |-- Healthy --> [Primary ALB/us-east-1] -> [App Pods + DB]
  |-- Unhealthy -> [Secondary ALB/us-west-2] -> [App Pods + Read Replica]
```

## Control Plane
- Health checks probe `/healthz` on both regions.
- Failover policy: primary -> secondary on 3/5 check failures.
- State sync: periodic backups replicated to secondary (stubbed with artifact generator in this pack).

## Data Plane
- RDS/Aurora multi-region read replica (conceptual) with delayed apply to prevent corruption.
- S3 cross-region replication for static assets.

## Security
- IAM roles scoped per region; deny cross-region writes except replication role.
- TLS termination at ALB; certs provisioned via ACM per region.
