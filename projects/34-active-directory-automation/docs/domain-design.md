# Active Directory Domain Design Document

**Domain:** corp.contoso.local
**NetBIOS:** CONTOSO
**Version:** 1.2
**Last Updated:** 2026-01-15
**Author:** Infrastructure Team

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Forest and Domain Architecture](#forest-and-domain-architecture)
3. [Domain Controller Placement](#domain-controller-placement)
4. [OU Structure Design](#ou-structure-design)
5. [Naming Conventions](#naming-conventions)
6. [Security Tier Model](#security-tier-model)
7. [Group Policy Architecture](#group-policy-architecture)
8. [GPO Inheritance Diagram](#gpo-inheritance-diagram)
9. [Delegation Model](#delegation-model)
10. [Group Strategy (AGDLP)](#group-strategy-agdlp)
11. [Password Policy Design](#password-policy-design)
12. [Service Account Standards](#service-account-standards)
13. [DNS Architecture](#dns-architecture)
14. [AD Replication Design](#ad-replication-design)
15. [Security Hardening Baseline](#security-hardening-baseline)
16. [Operational Runbooks](#operational-runbooks)

---

## Executive Summary

This document describes the Active Directory design for Contoso Corporation's `corp.contoso.local` domain. The design follows Microsoft's tier model for privileged access, uses a flat single-domain forest with role-based OU delegation, and enforces security via Group Policy and fine-grained password policies.

**Key Design Principles:**
- Single forest, single domain — simplicity and minimal trust complexity
- Tiered privilege model (Tier 0 / Tier 1 / Tier 2) to limit lateral movement
- All administrative actions performed from dedicated admin accounts, never from daily-use accounts
- Automation-first: DSC and Ansible maintain configuration drift-free state
- Full audit logging forwarded to SIEM (Elasticsearch)

---

## Forest and Domain Architecture

```
Forest: corp.contoso.local
└── Domain: corp.contoso.local  (Forest Root Domain)
    ├── Functional Level: Windows Server 2019
    ├── Domain Controllers: DC01, DC02
    └── Sites: HQ-Site
```

**Functional Levels**

| Level | Setting |
|-------|---------|
| Forest Functional Level | Windows Server 2019 |
| Domain Functional Level | Windows Server 2019 |
| Features Enabled | AD Recycle Bin, Privileged Access Management, KDS Root Key |

A single-domain design was chosen because:
- The organization has one geographic region
- No acquisition scenarios require separate trust boundaries
- Administrative simplicity reduces the attack surface

---

## Domain Controller Placement

| Host | IP | Site | FSMO Roles | Global Catalog | OS |
|------|-----|------|-----------|---------------|-----|
| DC01 | 192.168.10.10 | HQ-Site | PDC, RID, Schema, Naming | Yes | WS2022 |
| DC02 | 192.168.10.11 | HQ-Site | Infrastructure | Yes | WS2022 |

**DC Hardware Baseline:**
- CPU: 4 vCPUs minimum
- RAM: 8 GB minimum (16 GB recommended for large environments)
- NTDS disk: separate volume from OS, SSD-backed
- SYSVOL disk: separate volume preferred

**Recovery Objectives:**
- RTO (DC failure): < 30 minutes (DC02 takes PDC Emulator role automatically)
- RPO: Near-zero (replication interval 15 minutes, change notification enabled)

---

## OU Structure Design

The OU tree is organized by **object type at the top level** (Users, Computers, Service Accounts) with a **secondary split by department/function**. This allows GPO application at both the role level and the department level without complex WMI filters.

```
DC=corp,DC=contoso,DC=local
├── OU=IT
│   ├── OU=Admins          (Tier 1 admin accounts)
│   ├── OU=Help-Desk       (Tier 2 support accounts)
│   └── OU=DevOps          (CI/CD and automation engineers)
├── OU=HR
├── OU=Finance
├── OU=Operations
├── OU=ServiceAccounts     (Dedicated managed/standard service accounts)
├── OU=Servers
│   ├── OU=AppServers
│   ├── OU=WebServers
│   ├── OU=DBServers
│   └── OU=FileServers
├── OU=Workstations        (All end-user computers)
└── OU=Security            (Universal/DL groups used for resource access)
```

**Design Rationale:**

| OU | Purpose | GPO Applied |
|----|---------|-------------|
| IT/Admins | Tier 1 elevated accounts | IT-Admin-Rights, Baseline-Security |
| IT/Help-Desk | Password reset, ticket accounts | Help-Desk-Rights |
| IT/DevOps | CI/CD service + human accounts | DevOps-Access |
| HR | HR staff accounts | Workstation-Standard |
| Finance | Finance staff + AppLocker | Finance-AppLocker |
| Operations | Warehouse and logistics | Workstation-Standard |
| ServiceAccounts | svc-* accounts, no interactive logon | Service-Account-Policy |
| Servers | Computer objects for servers | Server-Hardening |
| Workstations | Computer objects for desktops/laptops | Workstation-Standard |
| Security | Resource access groups (AGDLP DL layer) | None |

---

## Naming Conventions

### User Accounts

| Type | Format | Example |
|------|--------|---------|
| Standard user | `{first initial}{surname}` | `jsmith` |
| Admin account (Tier 1) | `{first initial}{surname}-adm` | `jsmith-adm` |
| Service account | `svc-{function}` | `svc-backup` |
| gMSA account | `gmsa-{function}$` | `gmsa-iis$` |

### Computer Accounts

| Type | Format | Example |
|------|--------|---------|
| Domain Controller | `DC{2-digit-seq}` | `DC01`, `DC02` |
| Application server | `APP{2-digit-seq}` | `APP01` |
| Web server | `WEB{2-digit-seq}` | `WEB01` |
| Database server | `DB{2-digit-seq}` | `DB01` |
| File server | `FS{2-digit-seq}` | `FS01` |
| Workstation | `WS{3-digit-seq}` | `WS001` |

### Group Names (AGDLP Pattern)

| Layer | Format | Example |
|-------|--------|---------|
| Global (role) | `{Dept}-{Role}` | `IT-Admins`, `Finance-Users` |
| Domain Local (resource) | `DL-{Resource}-{Permission}` | `DL-FileShare-Read` |
| Universal (cross-domain) | `UG-{Function}` | `UG-VPN-Users` |

### GPO Names

Format: `{Scope}-{Function}-Policy`
Examples: `Baseline-Security-Policy`, `Workstation-Standard-Policy`, `Finance-AppLocker-Policy`

---

## Security Tier Model

Based on Microsoft's Enterprise Access Model:

```
┌────────────────────────────────────────────────────────────────┐
│  TIER 0 — Control Plane                                        │
│  Domain Controllers, AD Connect, PKI, DNS                      │
│  Admin accounts: dedicated DA accounts, accessed via PAW only  │
├────────────────────────────────────────────────────────────────┤
│  TIER 1 — Management Plane                                     │
│  Servers (App, Web, DB, File)                                  │
│  Admin accounts: jsmith-adm, mmartinez-adm                     │
│  Access via: jump server or privileged workstation             │
├────────────────────────────────────────────────────────────────┤
│  TIER 2 — User Plane                                           │
│  Workstations, end-user data, standard user sessions           │
│  Admin accounts: Help-Desk accounts for password resets only   │
└────────────────────────────────────────────────────────────────┘
```

**Key Rules:**
- Tier 0 accounts MUST NOT log in to Tier 1 or Tier 2 systems
- Tier 1 accounts MUST NOT log in to Tier 2 systems interactively
- Service accounts are scoped to the minimum required tier
- `Protected Users` security group applied to all Tier 0 and Tier 1 admin accounts

---

## Group Policy Architecture

### GPO Inventory

| GPO | Link Target | Enforced | Description |
|-----|-------------|----------|-------------|
| Default Domain Policy | Domain root | Yes | Password policy, account lockout |
| Baseline-Security-Policy | Domain root | Yes | NTLMv1 disable, SMBv1 disable, LDAP signing |
| Domain-Audit-Policy | Domain root | Yes | Advanced audit configuration |
| Workstation-Standard-Policy | OU=Workstations | No | Screensaver, removable media, desktop restrictions |
| Server-Hardening-Policy | OU=Servers | No | NLA for RDP, event log sizes, autorun disable |
| IT-Admin-Rights | OU=Admins,OU=IT | No | Local admin rights on servers via Restricted Groups |
| Help-Desk-Rights | OU=Help-Desk,OU=IT | No | Password reset delegation scope |
| Finance-AppLocker | OU=Finance | No | AppLocker whitelist for finance applications |

---

## GPO Inheritance Diagram

```
Domain Root (DC=corp,DC=contoso,DC=local)
│
├── [ENFORCED] Default Domain Policy
│     └── Password complexity, account lockout
│
├── [ENFORCED] Baseline-Security-Policy
│     └── LmCompatibilityLevel=5, NoLMHash=1, SMBv1=off, LDAP signing
│
├── [ENFORCED] Domain-Audit-Policy
│     └── Account logon, account management, logon/logoff, policy change
│
├── OU=IT
│   ├── OU=Admins
│   │     └── [APPLIED] IT-Admin-Rights
│   │           └── Local Administrators membership on server tier
│   └── OU=Help-Desk
│         └── [APPLIED] Help-Desk-Rights
│               └── Account unlock, password reset scope
│
├── OU=Finance
│     └── [APPLIED] Finance-AppLocker
│           └── Executable whitelist, script rules
│
├── OU=Servers
│     └── [APPLIED] Server-Hardening-Policy
│           └── NLA enforced, large event logs, autorun off
│
└── OU=Workstations
      └── [APPLIED] Workstation-Standard-Policy
            └── Screensaver timeout=15m, control panel locked,
                removable media blocked
```

---

## Delegation Model

Permissions are delegated at the OU level — no users have domain-wide admin rights except the built-in Administrator account (which is disabled for daily use).

| Delegated Permission | Delegate | Scope |
|---------------------|----------|-------|
| Full control of user objects | IT-Admins | OU=IT, OU=HR, OU=Finance, OU=Operations |
| Reset passwords, unlock accounts | Help-Desk | All user OUs |
| Create/delete computer accounts | IT-Admins | OU=Servers, OU=Workstations |
| Join computers to domain | svc-deploy | OU=Servers, OU=Workstations |
| Manage group membership | IT-Admins | OU=IT, OU=Security |
| Read all user attributes | svc-monitoring | Domain-wide (read only) |

---

## Group Strategy (AGDLP)

**Pattern:** Accounts → Global groups → Domain Local groups → Permissions

```
Example: Finance share access
  cwalker (Account)
    └── Finance-Users (Global group, OU=Finance)
          └── DL-FinanceShare-Read (Domain Local, OU=Security)
                └── NTFS Read permission on \\FS01\Finance
```

**Benefits:**
- Changes to resource permissions only require updating the Domain Local group
- Cross-domain group nesting is clean via Universal groups
- Auditing group membership changes is straightforward

---

## Password Policy Design

### Default Domain Policy

| Setting | Value |
|---------|-------|
| Minimum length | 14 characters |
| Maximum age | 90 days |
| Password history | 24 passwords |
| Complexity required | Yes |
| Reversible encryption | No |
| Lockout threshold | 5 attempts |
| Lockout duration | 30 minutes |
| Observation window | 30 minutes |

### Fine-Grained Password Policies

| PSO Name | Applies To | Min Length | Max Age | Lockout |
|----------|-----------|-----------|---------|---------|
| IT-Admins-PSO | IT-Admins group | 16 | 60 days | 3 attempts |
| ServiceAccounts-PSO | svc-* accounts | 24 | 365 days | Disabled |

---

## Service Account Standards

| Standard | Detail |
|----------|--------|
| Naming | `svc-{function}` for standard, `gmsa-{function}$` for gMSA |
| Location | OU=ServiceAccounts (dedicated OU, blocked from interactive logon GPO) |
| Password rotation | gMSA: automatic (every 30 days); standard svc-*: 365-day policy, rotate manually via runbook |
| Least privilege | Each account scoped to only the permissions it needs; never use Domain Admins for service accounts |
| Audit | All service account logon events sent to SIEM |
| Preferred type | gMSA for all new services supporting it (IIS, SQL, scheduled tasks) |

---

## DNS Architecture

| Zone | Type | Replication | Notes |
|------|------|-------------|-------|
| corp.contoso.local | Primary | Domain | Main AD-integrated zone |
| contoso.local | Primary | Domain | Legacy/short-name resolution |
| 10.168.192.in-addr.arpa | Primary | Domain | DC/server subnet reverse |
| 20.168.192.in-addr.arpa | Primary | Domain | Server VLAN reverse |
| 30.168.192.in-addr.arpa | Primary | Domain | Workstation VLAN reverse |

**Forwarders:** 8.8.8.8, 8.8.4.4 (internet resolution)
**Dynamic Updates:** Secure only on all AD-integrated zones
**Scavenging:** Enabled — no-refresh: 7 days, refresh: 7 days

---

## AD Replication Design

**Site:** HQ-Site (single site, all subnets)
**Schedule:** Always
**Interval:** 15 minutes
**Change Notification:** Enabled (immediate replication on change)
**Site Link Cost:** 100 (default)

Since all DCs are in the same physical site, replication uses the default intrasite topology (KCC-managed ring).

---

## Security Hardening Baseline

| Control | Implementation | Status |
|---------|---------------|--------|
| SMBv1 disabled | GPO + registry | Done |
| NTLMv1 disabled | LmCompatibilityLevel=5 | Done |
| LDAP signing required | LDAPServerIntegrity=2 | Done |
| LDAP channel binding | LdapEnforceChannelBinding=2 | Done |
| Kerberos AES-only | krbtgt encryption type | Done |
| AD Recycle Bin | Optional feature | Enabled |
| Protected Users group | Tier 0 + Tier 1 admins | Done |
| Fine-grained password policies | IT-Admins-PSO, ServiceAccounts-PSO | Done |
| Advanced audit policy | All categories | Done |
| LAPS | All workstations and servers | Planned |
| Privileged Access Workstations | Tier 0 admins | Planned |

---

## Operational Runbooks

### New User Onboarding

1. Create account in correct OU using `UsersAndGroups.ps1` DSC or `New-ADUser` wrapper script
2. Add to appropriate department group (HR-Users, Finance-Users, etc.)
3. Add to VPN-Users if remote access required
4. Confirm manager is set for delegation reporting
5. Trigger welcome email via HR system

### Account Offboarding

1. Disable account immediately
2. Move to `OU=Disabled` (create if needed) — do NOT delete for 90 days
3. Remove all group memberships
4. Reset password to 32-char random string
5. Revoke VPN certificates
6. After 90 days: archive mailbox, then delete AD object

### Password Reset (Help Desk)

1. Verify identity via manager or HR ticket
2. Use SSPR portal or `Unlock-ADAccount` + `Set-ADAccountPassword`
3. Set `ChangePasswordAtLogon = $true`
4. Log ticket with justification

### DC Failure Recovery

1. If DC01 fails: DC02 automatically serves all requests as GC
2. Seize FSMO roles to DC02: `Move-ADDirectoryServerOperationMasterRole -Identity DC02 -OperationMasterRole PDCEmulator,RIDMaster,InfrastructureMaster,SchemaMaster,DomainNamingMaster`
3. Rebuild DC01 from backup or promote new server
4. Transfer FSMO roles back when DC01 is healthy
