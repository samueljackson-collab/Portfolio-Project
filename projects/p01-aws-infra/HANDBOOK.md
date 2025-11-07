# Team Handbook — P01 (AWS Infrastructure Automation)

## Purpose & Scope
This handbook defines how the infrastructure team collaborates on AWS environment provisioning, change management, and disaster recovery operations. Covers communication norms, roles, and decision-making processes for CloudFormation-based infrastructure.

## Roles & RACI

| Task | Owner | Consulted | Informed |
|------|-------|-----------|----------|
| CloudFormation template design | Platform Engineer | Security, Network Team | DevOps Team |
| Stack deployment (dev/stage) | DevOps Engineer | Platform Engineer | Product Manager |
| Stack deployment (prod) | SRE Lead | Platform Engineer, Security | Engineering Org |
| DR drill execution | SRE Lead | Platform Engineer | VP Engineering |
| IAM policy review | Security Team | Platform Engineer | Compliance |
| Incident response | On-call SRE | Platform Team | Engineering Org |

## Working Agreements

### Standups & Cadence
- **Daily Standup**: 10:00 AM ET (async Slack updates acceptable)
- **Weekly Infrastructure Review**: Tuesdays 2:00 PM ET (review drift, costs, incidents)
- **Monthly DR Drill**: First Friday of month, 9:00 AM ET

### Definition of Ready (Infrastructure Changes)
- [ ] CloudFormation template validated (`cfn-lint`, `make validate`)
- [ ] Change request approved in Jira/Linear
- [ ] Impact analysis completed (affected services documented)
- [ ] Rollback plan documented

### Definition of Done
- [ ] Stack deployed successfully
- [ ] Smoke tests passing
- [ ] Documentation updated (RUNBOOK, ADRs)
- [ ] Change logged in CHANGELOG.md
- [ ] Monitoring alerts verified

## Communication

### Channels
- **Slack #infrastructure**: General infra questions, non-urgent updates
- **Slack #incidents**: Active incident coordination (P0/P1 only)
- **PagerDuty**: Critical alerts (RDS failover, stack rollback failures)

### SLAs
- **Non-urgent requests**: 1 business day response
- **Urgent (non-incident)**: 4 hours response
- **Incidents (P0/P1)**: Immediate acknowledgment (<5 min)

## Decision Records

### ADR Index
- [ADR-0001: Initial Technical Direction](./docs/ADR/0001-initial-decision.md)
- [ADR-0002: CloudFormation vs Terraform](./docs/ADR/0002-cfn-vs-terraform.md)
- [ADR-0003: Multi-AZ RDS Design](./docs/ADR/0003-multi-az-rds.md)

## Onboarding Checklist

### New Team Member Setup
- [ ] AWS Console access (via SSO)
- [ ] IAM role: `InfrastructureEngineer` (least privilege)
- [ ] Clone repository: `git clone <repo-url>`
- [ ] Install dependencies: `make setup`
- [ ] Run local validation: `make validate`
- [ ] Shadow a DR drill (observe only)
- [ ] Review last 3 incident postmortems
- [ ] Read all ADRs in `docs/ADR/`

### Access Requests
- **AWS Console**: Submit via Okta app catalog
- **PagerDuty**: Request from SRE lead
- **GitHub**: Join `infrastructure-team` org team
