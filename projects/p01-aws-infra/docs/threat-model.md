# Threat Model - P01 AWS Infrastructure

## System Overview
AWS infrastructure deployment including VPC networking, RDS database, and associated resources across 3 availability zones.

## Assets
1. **RDS Database** - Contains application data (High Value)
2. **VPC Configuration** - Network isolation and routing (Medium Value)
3. **IAM Roles and Policies** - Access control (High Value)
4. **CloudFormation/Terraform State** - Infrastructure configuration (High Value)
5. **Secrets** - Database credentials, API keys (Critical Value)

## Trust Boundaries
1. **Internet ↔ Public Subnets** - Public internet to AWS VPC
2. **Public Subnets ↔ Private Subnets** - DMZ to internal network
3. **Private Subnets ↔ RDS** - Application tier to data tier
4. **AWS Account ↔ User** - IAM authentication boundary
5. **Region ↔ Region** - Multi-region boundaries

## Threats (STRIDE Analysis)

### Spoofing
- **T1**: Attacker spoofs CloudFormation API calls
  - **Mitigation**: MFA required for infrastructure changes, AWS CloudTrail logging
- **T2**: Unauthorized IAM role assumption
  - **Mitigation**: ExternalId required for cross-account access, strict IAM policies

### Tampering
- **T3**: Modification of RDS data in transit
  - **Mitigation**: Encryption in transit enforced (SSL/TLS), certificate validation
- **T4**: Terraform state file tampering
  - **Mitigation**: S3 versioning enabled, DynamoDB locking, bucket access logging

### Repudiation
- **T5**: Infrastructure changes without attribution
  - **Mitigation**: CloudTrail enabled for all API calls, 90-day retention
- **T6**: Database query execution without logging
  - **Mitigation**: PostgreSQL logging enabled, log_statement='all'

### Information Disclosure
- **T7**: RDS data exposure through public access
  - **Mitigation**: RDS in private subnets only, no public access allowed
- **T8**: Credentials in version control
  - **Mitigation**: Secrets Manager for credentials, .gitignore for sensitive files
- **T9**: VPC Flow Logs exposure
  - **Mitigation**: CloudWatch Logs encryption, IAM policies restricting access

### Denial of Service
- **T10**: RDS connection exhaustion
  - **Mitigation**: Connection pooling, max_connections limit, CloudWatch alarms
- **T11**: NAT Gateway bandwidth saturation
  - **Mitigation**: Multiple NAT Gateways (one per AZ), CloudWatch monitoring
- **T12**: CloudFormation stack deletion
  - **Mitigation**: Stack termination protection, IAM policies, MFA for deletions

### Elevation of Privilege
- **T13**: Privilege escalation through IAM PassRole
  - **Mitigation**: IAM PassRole restrictions, permission boundaries
- **T14**: RDS superuser access compromise
  - **Mitigation**: Master user password in Secrets Manager, rotation policy
- **T15**: Container escape to host
  - **Mitigation**: N/A - no containers in this infrastructure layer

## Attack Trees

### Attack Goal: Access RDS Database
```
└─ Gain unauthorized access to RDS
   ├─ Compromise database credentials
   │  ├─ Extract from Secrets Manager [Requires IAM permissions]
   │  ├─ Find in version control [Mitigated by secrets scanning]
   │  └─ SQL injection [Application layer - out of scope]
   ├─ Network-level access
   │  ├─ Exploit public RDS endpoint [Mitigated - RDS in private subnet]
   │  ├─ Compromise bastion host [No bastion in this config]
   │  └─ VPN/Direct Connect access [Requires physical access]
   └─ Snapshot access
      ├─ Copy RDS snapshot [Requires IAM permissions + encryption key]
      └─ Access automated backup [Requires IAM permissions + encryption key]
```

## Security Controls

### Preventive Controls
- RDS in private subnets (no internet access)
- Security groups with least-privilege rules
- Encryption at rest (KMS) and in transit (TLS)
- IAM policies with least-privilege access
- MFA required for sensitive operations
- No hard-coded credentials

### Detective Controls
- CloudTrail logging all API calls
- VPC Flow Logs for network traffic
- CloudWatch alarms for anomalies
- RDS Enhanced Monitoring
- AWS Config rules for compliance

### Corrective Controls
- Automated backup retention (7 days)
- Multi-AZ for automatic failover
- Snapshot encryption enforced
- Incident response playbook (RUNBOOK.md)

## Residual Risks

| Risk | Likelihood | Impact | Mitigation Status | Acceptance Rationale |
|------|-----------|--------|-------------------|---------------------|
| Secrets Manager compromise | Low | High | Partially Mitigated | Requires extensive IAM compromise; monitoring in place |
| Insider threat | Low | High | Partially Mitigated | CloudTrail logging provides audit trail; no technical prevention |
| Multi-AZ failure | Very Low | High | Accepted | AWS infrastructure resilience; manual failover to backup region possible |
| State file corruption | Low | Medium | Mitigated | S3 versioning and DynamoDB locking prevent most scenarios |
| Cost overrun | Medium | Low | Monitored | CloudWatch billing alarms configured; acceptable business risk |

## Assumptions
1. AWS infrastructure is trustworthy and secure
2. IAM credentials are properly managed
3. Users follow security best practices
4. Network ACLs are properly configured
5. Application-layer security is handled separately

## Out of Scope
- Application-level vulnerabilities (handled in application security review)
- Physical security of AWS data centers (AWS responsibility)
- DDoS attacks (handled by AWS Shield)
- Zero-day vulnerabilities in AWS services

## Recommendations
1. Implement AWS Organizations SCPs for additional guardrails
2. Enable AWS GuardDuty for threat detection
3. Implement AWS Security Hub for centralized security findings
4. Regular security audits and penetration testing
5. Implement automated compliance checking (AWS Config)
6. Consider AWS Secrets Manager rotation for RDS credentials
