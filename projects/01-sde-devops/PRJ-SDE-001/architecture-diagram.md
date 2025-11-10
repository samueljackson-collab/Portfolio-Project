# Architecture Diagram Narrative

## Diagram Overview (Approx. 420 words)
The Mermaid diagram visualizes the AWS RDS PostgreSQL module within the boundaries of a single AWS Region (`us-west-2`). The outer orange box represents the regional perimeter, highlighting that all managed services remain inside the same compliance boundary. Nested inside is the blue VPC block with CIDR `10.20.0.0/16`, which is provisioned externally to the module but is required for deployment. Within the VPC we show two lavender private subnets—`10.20.10.0/24` in availability zone `us-west-2a` and `10.20.20.0/24` in `us-west-2b`. The primary RDS instance resides in the first subnet, while a synchronous standby replica lives in the second, reinforcing the Multi-AZ topology. Both database nodes use the green palette to signal the data tier, with inline annotations for storage encryption and the seven-day automated backup policy.

A pink security group node sits logically between the application tier and database resources. This node stresses that only TCP 5432 ingress from whitelisted application security groups is permitted, while egress is suppressed to minimize lateral movement. Adjacent AWS managed services—Secrets Manager and CloudWatch—are rendered in amber to indicate they are optional integrations delivered by AWS but orchestrated by Terraform outputs. The application tier, styled in yellow, sits outside the module boundary to clarify that workloads consuming the database are not provisioned here but must be accounted for to configure ingress rules. Finally, the external actor node represents Terraform runners or operators that execute plans and respond to alarms, showing how GitHub Actions or platform engineers interact with the system.

Directional arrows illustrate the numbered data flows. Terraform runners first create infrastructure and update the security group (Flow 1). Application traffic traverses from the workload security group into the database (Flows 2 and 3), where the primary instance replicates to the standby (Flow 4). Operational telemetry moves into CloudWatch (Flow 5), while credentials are retrieved from Secrets Manager (Flows 6 and 7). Alarm notifications return to operators (Flow 8). Inline notes call out security guardrails, cost awareness (~$1,250 per month for the production sizing), and performance expectations (<10 ms average read latency) so stakeholders can quickly infer service characteristics.

## Data Flow Walkthrough
1. **Terraform Apply:** CI/CD runner assumes the deployment IAM role, configures the security group, subnet group, and DB instance.
2. **Application Query:** Application containers on ECS or EC2 initiate TLS connections to port 5432 using credentials retrieved at runtime.
3. **Security Group Enforcement:** Traffic is evaluated against ingress rules; only pre-approved security groups succeed.
4. **Synchronous Replication:** The primary instance streams WAL records to the standby to guarantee a 60-second RTO.
5. **Metrics Emission:** CloudWatch receives CPU, storage, and connection metrics plus enhanced monitoring data.
6. **Credential Storage:** Module outputs feed Secrets Manager, which stores connection strings with rotation policies.
7. **Credential Retrieval:** Applications request secrets via IAM-authenticated API calls, ensuring no hard-coded passwords.
8. **Alarm Routing:** CloudWatch forwards alarms to PagerDuty/Slack where operators triage issues.

## Security Boundaries
- **Network Boundary:** Database subnets are private with no Internet Gateway route. Access requires belonging to an authorized security group.
- **IAM Boundary:** Terraform deployment role is scoped to RDS, EC2 security group, and Secrets Manager APIs. Applications authenticate via IAM roles to fetch secrets.
- **Data Boundary:** All data is encrypted at rest (KMS) and in transit (TLS 1.2+). Performance Insights retains metrics for auditing without exposing raw data.

## High Availability Design
- Multi-AZ replication provides automatic failover with Amazon RDS-managed DNS updates.
- Automated backups plus final snapshot enforcement ensure recoverability.
- Performance metrics and health probes detect anomalies early, and the standby remains hot with synchronous commit guaranteeing zero data loss within RPO targets.

## Cost Breakdown
| Component | Quantity | Monthly Estimate (us-west-2) |
|-----------|----------|------------------------------|
| RDS db.r6g.large (Multi-AZ) | 1 primary + 1 standby | $1,080 |
| Storage (500 GiB gp3) | 500 GiB | $55 |
| Backups (7-day retention) | 200 GiB | $20 |
| Performance Insights | Enabled | $10 |
| CloudWatch Logs & Metrics | 10 GB + alarms | $25 |
| **Total** | | **$1,190** |
