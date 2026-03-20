# Adversary Emulation Methodology

## Overview

This document explains the methodology used in this adversary emulation project,
including what adversary emulation is, how it differs from penetration testing,
and how the MITRE ATT&CK framework guides plan construction.

---

## What Is Adversary Emulation?

Adversary emulation is a **defensive security practice** in which a security team
replicates the known tactics, techniques, and procedures (TTPs) of a specific
threat actor to validate whether existing detection and response capabilities
would identify and alert on those behaviors.

The goal is **not** to compromise systems — it is to generate realistic telemetry
and verify that:

1. Detection rules trigger as expected
2. Alerts reach the correct analyst queues
3. Response playbooks are complete and accurate
4. Coverage gaps are identified before a real attack occurs

---

## Adversary Emulation vs. Penetration Testing

| Dimension | Adversary Emulation | Penetration Testing |
|-----------|--------------------|--------------------|
| **Goal** | Validate detection coverage | Find exploitable vulnerabilities |
| **Guided by** | Specific threat actor TTPs | OWASP, CVEs, attack surface |
| **Scope** | Known threat actor behavior | Full attack surface |
| **Output** | Detection gap report | Vulnerability report |
| **Audience** | Detection engineers, SOC | Security engineers, developers |
| **Risk** | Very low (safe tests) | Medium (real exploits used) |
| **Frequency** | Continuous / quarterly | Annual / on-demand |

Both practices are complementary and should be used together in a mature security program.

---

## The MITRE ATT&CK Framework

The [MITRE ATT&CK framework](https://attack.mitre.org) is a globally accessible
knowledge base of adversary tactics and techniques based on real-world observations.

### Structure

```
ATT&CK
└── Tactics (the "why" — 14 for Enterprise)
    ├── Initial Access
    ├── Execution
    ├── Persistence
    ├── Privilege Escalation
    ├── Defense Evasion
    ├── Credential Access
    ├── Discovery
    ├── Lateral Movement
    ├── Collection
    ├── Command and Control
    ├── Exfiltration
    └── Impact
        └── Techniques (the "how" — 200+ for Enterprise)
            └── Sub-techniques (specific implementation variants)
```

### Technique IDs

Each technique has a unique identifier:
- `T1566` — Phishing (technique)
- `T1566.001` — Spearphishing Attachment (sub-technique)
- `T1566.002` — Spearphishing Link (sub-technique)

### Threat Groups

ATT&CK documents known threat groups and their TTPs:
- `G0016` — APT29 (Cozy Bear / Nobelium)
- `G0046` — FIN7 (Carbanak)

These group pages list exactly which techniques each group uses, enabling
targeted emulation plans.

---

## How Emulation Plans Are Structured

Each emulation plan in this project follows a consistent YAML schema:

```yaml
name: <Threat Group> Emulation Plan
id: ep-<group>-v1
version: "1.0"
author: <analyst name>
date: <plan creation date>
description: >
  <Purpose and scope of this plan>
mitre_groups:
  - G00XX

phases:
  - id: phase-N
    name: <MITRE Tactic Name>
    description: >
      <How this threat actor implements this tactic>
    techniques:
      - id: TXXXX.XXX          # MITRE ATT&CK ID
        name: <Technique Name>
        tactic: <tactic slug>
        test_id: AT-XXX        # Unique test identifier
        test_name: <Human-readable test name>
        description: >
          <What this test simulates and why>
        command: "<safe shell command>"
        expected_detection: <What the detection should alert on>
        detection_rule: <path to Sigma rule>
        safe: true             # Always true in this project
        cleanup: "<cleanup command>"
        references:
          - https://attack.mitre.org/techniques/TXXXX/
```

### Key Fields

| Field | Purpose |
|-------|---------|
| `id` | MITRE ATT&CK technique ID (links to documentation) |
| `test_id` | Local identifier for tracking in test management systems |
| `command` | The safe shell command that generates detectable telemetry |
| `expected_detection` | What a SIEM/EDR rule should alert on |
| `detection_rule` | Relative path to associated Sigma detection rule |
| `safe` | Boolean — must be `true` for all tests in this project |
| `cleanup` | Command to remove any artifacts created by the test |

---

## Using Plans with Detection Engineering

### Workflow

```
1. Select Plan
   └── Choose threat actor relevant to your organization's threat model

2. Review Tests
   └── python atomic_executor.py --plan apt29 --list-phases

3. Dry Run
   └── python atomic_executor.py --plan apt29 --dry-run

4. Execute (Safe Mode)
   └── python atomic_executor.py --plan apt29 --safe

5. Check Detections
   └── Review SIEM/EDR for expected alerts

6. Document Gaps
   └── Record which detections fired and which did not

7. Develop Missing Rules
   └── Write Sigma rules for gaps, test, deploy

8. Re-run Plan
   └── Validate new rules fire correctly
```

### Integration with SIEM Platforms

Detection rules referenced in emulation plans use Sigma format, which can
be converted to queries for major SIEM platforms:

```bash
# Convert Sigma rule to Splunk SPL
sigma convert -t splunk sigma/suspicious-double-extension-file.yml

# Convert to Elastic EQL
sigma convert -t elastic_eql sigma/suspicious-double-extension-file.yml

# Convert to Microsoft Sentinel KQL
sigma convert -t kusto sigma/suspicious-double-extension-file.yml
```

### Measuring Detection Coverage

After running an emulation plan, calculate your coverage score:

```
Coverage Score = (Detections Fired / Total Tests) × 100
```

Example results:
- 20/24 tests triggered detection = 83% coverage
- Document the 4 gaps and create detection rules
- Re-run to validate new coverage

---

## Safety Guidelines

All tests in this project strictly follow these safety rules:

### What These Tests DO

- Write informational text files to `/tmp`
- Read world-readable system files (`/etc/passwd`, `/etc/hosts`, `/etc/os-release`)
- Read environment variables (`$USER`, `$HOME`, `$PATH`)
- Execute built-in commands (`echo`, `cat`, `ls`, `id`, `hostname`, `printenv`)
- Create and immediately delete small test files

### What These Tests DO NOT DO

- Execute actual exploit code
- Modify system files outside `/tmp`
- Create network connections
- Attempt privilege escalation
- Install software or modify configurations
- Access files outside the tester's own permissions
- Require root or elevated privileges

### Before Running Tests

1. Obtain written authorization from the system owner
2. Notify the SOC that emulation tests are running
3. Define a test window (start/end time)
4. Keep a rollback plan
5. Test in a non-production environment first
6. Use `--dry-run` mode to preview before executing

### Documentation Requirements

Always document:
- Authorization obtained (from whom, date)
- Test window (start/end)
- Systems tested
- All commands executed
- All artifacts created
- All cleanup actions taken

---

## Threat Model Alignment

When selecting emulation plans, consider your organization's threat model:

| Organization Type | Recommended Plans |
|-------------------|------------------|
| Government / Defense | APT29, APT28, APT41 |
| Financial Services | FIN7, FIN8, Carbanak |
| Healthcare | Wizard Spider (Ryuk), Conti |
| Technology | Lazarus Group, APT10 |
| Retail / Hospitality | FIN7, FIN6 |
| Energy / ICS | Sandworm, Triton/TRISIS |

---

## References

- [MITRE ATT&CK Framework](https://attack.mitre.org)
- [ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/)
- [Sigma Detection Rules](https://github.com/SigmaHQ/sigma)
- [MITRE CALDERA (automated emulation)](https://caldera.mitre.org)
- [Atomic Red Team (test library)](https://atomicredteam.io)
- [CISA Adversary Emulation Guidance](https://www.cisa.gov/resources-tools/resources/adversary-emulation)
