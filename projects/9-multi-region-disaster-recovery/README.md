# Project 9: Multi-Region Disaster Recovery Automation

## Overview
This project provisions a resilient architecture with automated failover between AWS regions. It synchronizes stateful services, validates replication health, and performs controlled recovery drills.

## Architecture
- **Context:** Mission-critical services must remain available during regional outages with minimal RTO/RPO and predictable failover/fallback runbooks.
- **Decision:** Use active-passive topology with Route53 health checks, Aurora Global Database, cross-region S3 replication, and standby compute in a paired region, orchestrated by SSM automation and chaos drills.
- **Consequences:** Provides deterministic failover but doubles some infrastructure cost and demands continuous replication health monitoring plus controlled drill cadence.

[Mermaid source](assets/diagrams/architecture.mmd) · Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

## Components
- Terraform stack that deploys networking, Aurora Global Database, Route53 health checks, and asynchronous replication.
- AWS Systems Manager Automation runbook for failover.
- Chaos experiment harness to validate RTO/RPO targets.

## Usage
```bash
cd terraform
terraform init
terraform apply -var-file=production.tfvars

# Execute failover drill
../scripts/failover-drill.sh
```

## Runbooks
Detailed runbooks for failover, fallback, and DR testing are located in the `runbooks/` directory.
