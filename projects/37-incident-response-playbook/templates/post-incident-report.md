# Post-Incident Report (PIR) — Example

**Incident ID:** INC-2026-0042
**Incident Type:** Ransomware — LockBit 3.0
**Severity:** P1 — Critical
**PIR Date:** 2026-01-20
**Report Author:** SOC Lead / IR Team
**Status:** CLOSED

---

## Executive Summary

On 2026-01-15 at 08:14 UTC, a LockBit 3.0 ransomware infection was detected on three Windows
servers in the Finance VLAN. The initial access vector was a phishing email containing a malicious
Word document (CVE-2024-21413 exploit). The infection was contained within 47 minutes of detection.
No data was exfiltrated. All affected systems were restored from backup within 6 hours.

**MTTD:** 22 minutes | **MTTC:** 47 minutes | **MTTR:** 6 hours 14 minutes

---

## Incident Timeline

| Time (UTC) | Event |
|-----------|-------|
| 2026-01-15 07:52 | User jsmith@corp.com opens malicious Word attachment (INC-2026-0042-email.msg) |
| 2026-01-15 07:54 | WINWORD.EXE spawns PowerShell; EDR generates medium-severity alert |
| 2026-01-15 08:01 | Lateral movement via PsExec to FIN-SRV-01 and FIN-SRV-02 |
| 2026-01-15 08:03 | Volume Shadow Copy deletion on FIN-SRV-01 (vssadmin.exe) |
| 2026-01-15 08:07 | First encrypted files detected (.lockbit extension) — EDR escalates to HIGH |
| 2026-01-15 08:14 | SOC Analyst ALERT-acknowledged; IC declared; bridge call opened |
| 2026-01-15 08:29 | All 3 affected hosts isolated via CrowdStrike console |
| 2026-01-15 08:41 | Perimeter block list updated (C2 IPs blocked) |
| 2026-01-15 09:01 | Containment confirmed — no further spread detected |
| 2026-01-15 09:15 | Forensic image of FIN-SRV-01 captured |
| 2026-01-15 11:30 | Root cause confirmed: CVE-2024-21413 + weak MFA on jsmith account |
| 2026-01-15 14:28 | FIN-SRV-01 restored from 2026-01-14 backup — validated |
| 2026-01-15 14:44 | FIN-SRV-02 restored |
| 2026-01-15 14:55 | jsmith workstation rebuilt from golden image |

---

## Root Cause Analysis

**5-Why Analysis:**

1. Why were files encrypted?
   → Ransomware executed with SYSTEM privileges on Finance servers.

2. Why could it execute with SYSTEM privileges?
   → Lateral movement succeeded via PsExec using jsmith's domain admin credentials.

3. Why did jsmith have domain admin credentials?
   → Role creep: ticket INC-2024-0891 granted temp domain admin, never revoked.

4. Why was the malicious document opened?
   → EDR did not block macro execution in Protected View (policy misconfiguration).

5. Why did Protected View not block it?
   → Registry key `HKCU\Software\Microsoft\Office\16.0\Word\Security\ProtectedView\DisableInternetFilesInPV` set to 1 (set by a legacy app install script in 2023).

---

## Affected Assets

| Asset | Type | Impact | Recovery Method | RTO Achieved |
|-------|------|--------|-----------------|-------------|
| FIN-SRV-01 | Windows Server 2022 | Full encryption | Restore from backup | 6h 14m |
| FIN-SRV-02 | Windows Server 2022 | Partial encryption | Restore from backup | 6h 30m |
| JSMITH-WS | Windows 11 workstation | Full encryption | Golden image rebuild | 4h 45m |

---

## Control Failures

| Control | Failure | Remediation |
|---------|---------|-------------|
| Least privilege | jsmith had unneeded domain admin | Privileged Access Management (PAM) review |
| Office macro policy | DisableInternetFilesInPV = 1 | GPO remediation applied 2026-01-16 |
| MFA | jsmith had SMS MFA (bypassable) | FIDO2 rollout for all privileged users |
| EDR policy | Alert threshold too high (missed PowerShell) | Policy tuned; alert threshold lowered |

---

## Action Items

| # | Action | Owner | Due Date | Status |
|---|--------|-------|----------|--------|
| 1 | PAM review — remove unneeded admin rights (all users) | IT Security | 2026-02-14 | OPEN |
| 2 | GPO: enforce Protected View for all Office installations | SysAdmin | 2026-01-23 | CLOSED |
| 3 | FIDO2 MFA for all domain admin accounts | IT Security | 2026-02-07 | IN PROGRESS |
| 4 | Tabletop exercise — ransomware scenario | SOC Lead | 2026-03-15 | OPEN |
| 5 | Backup validation automation (weekly test restore) | Infra | 2026-02-28 | OPEN |

---

## Metrics

| Metric | Value | Target | Pass/Fail |
|--------|-------|--------|-----------|
| MTTD (Mean Time to Detect) | 22 min | < 60 min | ✅ PASS |
| MTTC (Mean Time to Contain) | 47 min | < 2 hours | ✅ PASS |
| MTTR (Mean Time to Recover) | 6h 14m | < 8 hours | ✅ PASS |
| Data exfiltration | None | None | ✅ PASS |
| Customer impact | None | None | ✅ PASS |

---

## Recommendations

1. **Privileged Access Workstations (PAWs):** Require all domain admins to use dedicated hardened workstations for privileged tasks.
2. **Canary files:** Deploy honeypot files in high-value shares to detect ransomware earlier.
3. **Network micro-segmentation:** Finance VLAN should not allow lateral SMB/RDP from user workstations.
4. **Immutable backups:** Migrate backup sets to write-once S3 Object Lock to prevent backup encryption.
