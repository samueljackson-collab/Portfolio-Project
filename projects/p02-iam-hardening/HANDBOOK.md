# Team Handbook — P02 (IAM Security Hardening)

## Purpose & Scope
Defines security team collaboration on IAM policy management, access reviews, and compliance automation.

## Roles & RACI

| Task | Owner | Consulted | Informed |
|------|-------|-----------|----------|
| IAM policy design | Security Engineer | Platform Team | Compliance |
| Access Analyzer review | Security Lead | InfoSec | Engineering |
| Policy deployment | Security Engineer | Platform Engineer | DevOps Team |
| Access revocation | Security Lead | Manager | Affected User |

## Working Agreements

### Standups & Cadence
- **Weekly IAM Review**: Thursdays 10:00 AM ET
- **Monthly Access Audit**: First Monday of month
- **Quarterly Compliance Review**: With audit team

### Definition of Ready (Policy Changes)
- [ ] Policy validated (`make validate-policies`)
- [ ] Simulated with test cases
- [ ] Security review completed
- [ ] Change ticket approved

### Definition of Done
- [ ] Policy deployed to AWS
- [ ] Access Analyzer scan completed (no new findings)
- [ ] Documentation updated
- [ ] CHANGELOG.md entry added

## Communication

### Channels
- **Slack #security**: General security questions
- **Slack #security-incidents**: Active security events
- **Email**: Formal access requests

### SLAs
- **Access requests**: 2 business days
- **Critical findings**: 4 hours response
- **P0 security incidents**: Immediate

## Decision Records
- [ADR-0001: Least-Privilege Policy Design](./docs/ADR/0001-least-privilege.md)

## Onboarding Checklist
- [ ] AWS Console access (SecurityAuditor role)
- [ ] Complete IAM security training
- [ ] Shadow an access review
- [ ] Read last 3 Access Analyzer reports
