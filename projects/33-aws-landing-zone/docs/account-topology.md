# AWS Landing Zone — Account Topology

## Organization Hierarchy

```
AWS Organization: o-abc1234567
└── Root (r-ab12)
    ├── Management Account (123456789000)  [Master payer, billing, Organizations]
    │
    ├── Security OU (ou-ab12-sec00001)
    │   ├── Account: security-audit   (123456789012)
    │   └── Account: log-archive      (234567890123)
    │
    ├── Infrastructure OU (ou-ab12-inf00001)
    │   └── Account: shared-services  (345678901234)
    │
    ├── Workloads OU (ou-ab12-wrk00001)
    │   ├── Production OU (ou-ab12-prd00001)
    │   │   └── [Future: prod-workload accounts]
    │   └── Non-Production OU (ou-ab12-npd00001)
    │       └── [Future: dev/staging workload accounts]
    │
    └── Sandbox OU (ou-ab12-sbx00001)
        └── Account: sandbox-dev      (456789012345)
```

---

## Account Purposes

| Account          | OU             | Account ID    | Purpose                                      | Billing Access |
|------------------|----------------|---------------|----------------------------------------------|----------------|
| Management       | Root           | 123456789000  | AWS Organizations master payer, SSO config   | Full           |
| security-audit   | Security       | 123456789012  | GuardDuty master, SecurityHub aggregator     | Denied         |
| log-archive      | Security       | 234567890123  | Centralized CloudTrail + Config log bucket   | Denied         |
| shared-services  | Infrastructure | 345678901234  | Transit Gateway, DNS, CI/CD, artifact stores | Denied         |
| sandbox-dev      | Sandbox        | 456789012345  | Developer experimentation, auto-cleanup      | Allowed        |

---

## Access Matrix

| Permission Set       | Management | security-audit | log-archive | shared-services | sandbox-dev |
|----------------------|:----------:|:--------------:|:-----------:|:---------------:|:-----------:|
| AdministratorAccess  | Platform   | —              | —           | Platform        | —           |
| ReadOnlyAccess       | —          | Auditors       | Auditors    | —               | —           |
| DevOpsAccess         | —          | —              | —           | DevOps          | DevOps      |
| SecurityAuditAccess  | —          | Security       | —           | —               | —           |

Legend: **Platform** = Platform Engineering team | **Auditors** = External/internal auditors |
**DevOps** = Application/DevOps engineers | **Security** = Security team

---

## SCPs Applied by Scope

| SCP Policy               | Scope               | Effect                                           |
|--------------------------|---------------------|--------------------------------------------------|
| DenyRootActions          | Root (all accounts) | Blocks billing portal + root MFA device changes  |
| RequireMFA               | Root (all accounts) | Enforces MFA for IAM writes and role assumption  |
| RestrictRegions          | Workloads OU        | Limits API calls to us-east-1, us-west-2, eu-west-1 |
| DenyInternetGateways     | Security OU         | Prevents IGW attachment/creation                 |

---

## Naming Convention

### Accounts

Pattern: `<purpose>-<qualifier>`

Examples:
- `security-audit` — Security tooling, audit functions
- `log-archive` — Centralized log storage
- `shared-services` — Shared platform infrastructure
- `prod-workload-ecommerce` — Production account for a specific workload
- `sandbox-dev` — Developer sandbox

### Organizational Units

Pattern: `<function>` at root level, `<function>-<subtype>` for nested OUs

Examples:
- `Security`, `Infrastructure`, `Workloads`, `Sandbox` (root level)
- `Workloads/Production`, `Workloads/Non-Production` (nested)

### IAM Roles (cross-account)

| Role Name                         | Purpose                                      |
|-----------------------------------|----------------------------------------------|
| `OrganizationAccountAccessRole`   | Cross-account assume-role from management    |
| `AWSControlTowerExecution`        | Reserved for Control Tower automation        |
| `TerraformExecutionRole`          | Terraform plans/applies via CI/CD            |
| `SecurityAuditReadRole`           | Cross-account read for security tooling      |

---

## Network Segmentation Design

```
┌─────────────────────────────────────────────────────────────────┐
│  AWS Network Architecture                                        │
│                                                                  │
│  shared-services (345678901234)                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Transit Gateway (tgw-0123456789abcdef0)                 │    │
│  │  ├── Attachment: Security OU VPCs (isolated route table) │    │
│  │  ├── Attachment: Workloads VPCs (workload route table)   │    │
│  │  └── Attachment: Shared Services VPC (hub route table)   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  VPC CIDR Allocation:                                            │
│  ├── 10.0.0.0/16  — shared-services (hub VPC)                   │
│  ├── 10.10.0.0/16 — security-audit  (isolated, no IGW)          │
│  ├── 10.20.0.0/16 — log-archive     (isolated, no IGW)          │
│  ├── 10.100.0.0/8 — Workloads/Prod  (routable, NAT only)        │
│  └── 172.16.0.0/12 — Sandbox        (internet via IGW allowed)  │
│                                                                  │
│  Egress Strategy:                                                │
│  - Security OU:   No internet access (SCP: DenyInternetGateways)│
│  - Workloads Prod: NAT Gateway only (no direct IGW)              │
│  - Sandbox:        Direct IGW allowed for developer access       │
│  - Shared Services: NAT + VPN endpoint for on-prem connectivity  │
└─────────────────────────────────────────────────────────────────┘
```

### Route Table Design

| Account / OU     | Internet Access | Route to On-Prem | Route to Shared Services |
|------------------|:--------------:|:-----------------:|:------------------------:|
| security-audit   | None (SCP)     | Via TGW + VPN    | Via TGW                  |
| log-archive      | None (SCP)     | Via TGW + VPN    | Via TGW                  |
| shared-services  | NAT Gateway    | VPN / Direct     | Local                    |
| Workloads/Prod   | NAT Gateway    | Via TGW + VPN    | Via TGW                  |
| Workloads/NonProd| NAT Gateway    | Via TGW          | Via TGW                  |
| sandbox-dev      | IGW allowed    | None             | Via TGW (optional)       |

---

## Tag Policy

All resources must include the following mandatory tags:

| Tag Key       | Example Values                      | Enforced By |
|---------------|-------------------------------------|-------------|
| `Environment` | prod, staging, dev, sandbox         | Tag Policy  |
| `Owner`       | platform-team, security-team        | Tag Policy  |
| `CostCenter`  | CC-1234                             | Tag Policy  |
| `ManagedBy`   | terraform, cloudformation, manual   | Convention  |
| `Project`     | landing-zone, ecommerce, data-lake  | Convention  |

---

## Account Vending Process

When a new workload account is requested:

1. Submit account request (JIRA ticket or ServiceNow form)
2. Platform team reviews and approves
3. Terraform automation creates `aws_organizations_account` in the correct OU
4. Account Baseline runs via CodePipeline:
   - Enables CloudTrail → ships to log-archive S3
   - Enables Config → ships findings to security-audit
   - Creates standard IAM roles (TerraformExecutionRole, etc.)
   - Attaches to Transit Gateway
   - Applies mandatory resource tags
5. SSO groups mapped to the new account
6. Account details communicated to the requesting team

Estimated lead time: **< 30 minutes** (fully automated)
