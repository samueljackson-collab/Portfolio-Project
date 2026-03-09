# Samuel Jackson
**Cybersecurity Analyst & Security Operations Specialist**

📍 Seattle, WA | 📧 samuel.jackson@example.com | 📞 (555) 123-4567
🔗 [GitHub](https://github.com/samueljackson-collab) | 🔗 [Portfolio](https://samueljackson.dev)

---

## Professional Summary

Security-focused engineer with hands-on experience in threat detection, security monitoring, incident response, and defensive infrastructure hardening. Combines deep systems and network knowledge with security operations practices to detect, investigate, and respond to threats. Experienced in building SIEM-ready log pipelines, implementing IDS/IPS, conducting vulnerability assessments, and executing structured incident response procedures. Passionate about defense-in-depth and measurable security posture improvement.

---

## Technical Skills

**Security Operations:** SIEM log analysis, intrusion detection, alert triage, incident response, threat hunting
**IDS/IPS:** Suricata (inline IPS mode), rule tuning, alert correlation, network traffic analysis
**Log Management:** Loki, Promtail, Rsyslog, structured log aggregation, log-driven threat detection
**Monitoring & Alerting:** Prometheus, Grafana (security dashboards), Alertmanager, PagerDuty integration
**Vulnerability Management:** tfsec (IaC scanning), OWASP Top 10 awareness, network exposure assessment
**Network Security:** VLAN segmentation, firewall policy management, default-deny ACLs, VPN (WireGuard)
**Identity & Access:** FreeIPA, LDAP, RADIUS, MFA enforcement, least-privilege access control
**Cloud Security:** AWS IAM policies, security groups, KMS encryption, CIS AWS Foundations Benchmark
**Forensics & Analysis:** Log correlation, packet capture analysis, timeline reconstruction
**Automation:** Python, Bash scripting, Ansible (security playbooks), Terraform (IaC security controls)
**Frameworks:** NIST Cybersecurity Framework, MITRE ATT&CK (foundational), CIS Controls

---

## Professional Experience

### Desktop Support Technician — 3DM, Redmond, WA
**February 2025 – Present**

- Monitor and respond to endpoint security alerts, escalating suspicious activity per documented procedures
- Enforce MFA configuration and review Active Directory account permissions for least-privilege compliance
- Investigate phishing attempts and suspicious email attachments, coordinating with IT security team
- Maintain audit trail documentation for account provisioning, deprovisioning, and access changes
- Apply OS and application security patches following change management procedures

### Freelance IT & Web Manager — Self-Employed
**2015 – 2022**

- Conducted quarterly security reviews of client network configurations and firewall rulesets
- Implemented DNS filtering (Pi-hole) blocking malicious domains across 5+ client environments
- Performed WordPress security hardening: plugin audits, file permission reviews, login protections
- Investigated 3 security incidents (brute-force attacks, malware injections), executed remediation
- Deployed SSL certificates and enforced HTTPS across all client web properties

**Security Incident Response Experience:**
- **Brute-force attack:** Identified via access log analysis, blocked source IPs, implemented fail2ban
- **Malware injection:** Detected via file integrity monitoring, cleaned infected files, hardened permissions
- **Unauthorized access attempt:** Correlated VPN logs with failed authentication events, updated ACLs

---

## Security Projects & Portfolio

### Network Intrusion Detection & Prevention (Suricata IPS)
*Security Operations | Suricata, pfSense, Loki | October 2024*

- Deployed Suricata in inline IPS mode on internet-facing network interface
- Configured Emerging Threats ruleset with custom tuning to reduce false positives
- Forwarded Suricata alerts to Loki for centralized SIEM-ready log retention
- Created Grafana dashboards correlating IPS alerts with network traffic anomalies
- Documented alert response runbooks for common attack patterns (port scans, brute-force, C2 beacons)

**Detection Coverage:**
| Category | Detection Method | Avg Daily Alerts |
|----------|----------------|-----------------|
| Port Scanning | Suricata + firewall logs | 15-30 |
| Brute-force | Auth log correlation | 5-20 |
| Malicious DNS | Pi-hole + Loki | 50-100 |
| Suspicious Outbound | Suricata egress rules | 2-5 |
| Known Bad IPs | Threat intel feed | 10-20 |

**Evidence:** [Network Security Configuration](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/06-homelab/PRJ-HOME-001/assets)

---

### Security Operations Center (SOC) Simulation — Portfolio App
*Security Engineering | FastAPI, Python, Prometheus | 2024*

- Built SOC simulation components demonstrating threat detection, alert triage, and incident workflows
- Implemented red team simulation endpoints covering vulnerability scanning and attack chain emulation
- Created EDR simulation showcasing endpoint behavior analysis and threat containment
- Built ransomware simulation demonstrating detection patterns (file entropy, I/O anomalies)
- Designed threat hunting interface with structured query patterns against log data

**Simulation Modules:**
- **Red Team:** Reconnaissance, lateral movement, privilege escalation simulation patterns
- **SOC Analyst:** Alert queue management, triage workflow, case escalation
- **EDR:** Process behavior analysis, file operation monitoring, network connection tracking
- **Threat Hunting:** Hypothesis-driven search across logs using MITRE ATT&CK techniques
- **Malware Analysis:** Static/behavioral indicators, sandbox output interpretation

**Evidence:** [Security Simulators](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/frontend/src/components)

---

### Centralized Log Management & SIEM-Ready Pipeline
*Security Engineering | Loki, Promtail, Rsyslog | November 2024*

- Deployed centralized log aggregation pipeline ingesting logs from 10+ infrastructure sources
- Configured Promtail with structured parsing for access logs, auth logs, and system events
- Built security-focused Loki queries for failed authentication, sudo escalation, and config changes
- Implemented log retention policy with 90-day hot storage and 1-year cold archive
- Created Grafana security dashboards surfacing authentication anomalies and access patterns

**Log Sources Integrated:**
| Source | Log Type | Security Value |
|--------|---------|----------------|
| Linux syslog | Auth, sudo, kernel | Privilege escalation detection |
| Nginx access logs | HTTP requests | Web attack pattern detection |
| FreeIPA/LDAP | Authentication events | Identity threat detection |
| Suricata | Network IPS alerts | Network-layer threat detection |
| pfSense/UDM | Firewall deny logs | Lateral movement detection |

**Evidence:** [Observability Stack](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/01-sde-devops/PRJ-SDE-002/assets)

---

### Infrastructure Security Hardening (AWS & IaC)
*Cloud Security | Terraform, tfsec, CIS Benchmarks | August 2024*

- Implemented security controls for AWS RDS deployment: encryption at rest (KMS), private subnets, security groups
- Achieved 95% compliance with CIS AWS Foundations Benchmark via Terraform configuration
- Integrated tfsec scanning in CI/CD pipeline to block insecure IaC changes pre-deployment
- Configured IAM policies with least-privilege principle, no wildcard actions or resource ARNs
- Implemented automated backup with encryption and point-in-time recovery capability

**Security Controls Applied:**
- Encryption: KMS-managed keys for RDS, S3, and EBS volumes
- Network: Private subnets only, no public IP assignment, VPC flow logs enabled
- IAM: Resource-specific policies, condition keys, no hardcoded credentials
- Audit: CloudTrail enabled, S3 access logging, CloudWatch metric filters

**Evidence:** [Terraform Security Module](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/01-sde-devops/PRJ-SDE-001)

---

## Incident Response Framework

### Structured Response Approach (PICERL)

```
Preparation → Identification → Containment → Eradication → Recovery → Lessons Learned
     ↑                                                                        │
     └────────────────────── Continuous Improvement ─────────────────────────┘
```

**Runbooks Developed:**
- Security Incident Response (detection → escalation → containment → recovery)
- Brute-force Attack Response (log analysis → IP block → account lock review)
- Web Application Attack Response (access log review → WAF update → patch assessment)
- Ransomware Response (isolation → backup validation → recovery → forensics)

**Evidence:** [Security Runbooks](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/docs/runbooks)

---

## Education

**Bachelor of Science in Information Systems**
Colorado State University | 2016 – 2024

**Relevant Coursework:** Network Security, Information Security Management, Database Security, Risk Assessment, Ethical Hacking Fundamentals

---

## Certifications & Training

- **CompTIA Security+** *(study in progress — exam targeted Q2 2025)*
- **AWS Certified Security – Specialty** *(planned — cloud security focus)*
- **CompTIA CySA+** *(planned — SOC analyst validation)*
- **MITRE ATT&CK Fundamentals** *(self-study, applying framework to detection engineering)*

---

## Key Achievements

- **Threat Detection:** Suricata IPS blocking 50-100 malicious connection attempts daily with custom alert rules
- **Incident Response:** Successfully investigated and remediated 3 client security incidents with zero data loss
- **Security Posture:** Achieved 95% CIS AWS Foundations Benchmark compliance via automated IaC controls
- **Zero Trust Network:** Implemented 5-VLAN segmentation with default-deny policy and zero cross-VLAN breaches
- **Log Visibility:** Centralized logs from 10+ sources enabling correlation-based threat detection

---

## What I Bring to Security Operations

- **Defense-in-Depth:** Layer multiple controls so no single failure exposes the environment
- **Hypothesis-Driven Hunting:** Threat hunt with specific ATT&CK technique hypotheses, not random searching
- **Logging Discipline:** If it's not logged and retained, it can't be investigated
- **Documentation:** Runbooks that work under pressure, written for responders not authors
- **Systems Context:** Understanding how infrastructure works helps distinguish anomalies from normal behavior
- **Continuous Improvement:** Every incident generates a lessons-learned that updates detection and response
