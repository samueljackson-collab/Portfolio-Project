# Samuel Jackson
**Network Engineer & Datacenter Operations Specialist**

📍 Seattle, WA | 📧 samuel.jackson@example.com | 📞 (555) 123-4567
🔗 [GitHub](https://github.com/samueljackson-collab) | 🔗 [Portfolio](https://samueljackson.dev)

---

## Professional Summary

Network engineer with hands-on experience designing, implementing, and operating enterprise-grade network infrastructure in both homelab and client environments. Proven ability to architect VLAN-segmented networks, configure stateful firewalls, manage wireless infrastructure, and implement secure remote access solutions. Strong foundation in network monitoring, troubleshooting methodologies, and datacenter infrastructure operations. Combines deep technical knowledge with clear documentation practices for repeatable, auditable network management.

---

## Technical Skills

**Network Hardware:** UniFi Dream Machine Pro, UniFi Pro Switches (24/48 port PoE), UniFi Access Points (U6+), pfSense
**Protocols & Standards:** TCP/IP, DNS, DHCP, VLAN (802.1Q), VPN (WireGuard, OpenVPN), OSPF, STP, LACP
**Wireless:** WPA3 Enterprise, 802.1X RADIUS authentication, RF planning, SSID segmentation
**Security:** Suricata IDS/IPS, firewall policy management, default-deny ACLs, network segmentation, DNSSEC
**Monitoring:** SNMP, Prometheus (node_exporter, SNMP exporter), Grafana network dashboards, Loki log aggregation
**Identity & Access:** FreeIPA, Active Directory, LDAP, RADIUS (FreeRADIUS)
**Virtualization:** Proxmox VE, LXC containers, network bridges, VLANs on hypervisors
**Automation:** Ansible (network playbooks), Bash, Python, Terraform
**Documentation:** Mermaid network diagrams, Visio-equivalent flowcharts, runbooks

---

## Professional Experience

### Desktop Support Technician — 3DM, Redmond, WA
**February 2025 – Present**

- Troubleshoot Layer 2/3 connectivity issues for Windows/Mac workstations across campus network
- Configure and validate VPN access for remote employees, coordinating with network team
- Manage VLAN assignments and switch port configurations for new workstation deployments
- Document network topology changes and update configuration baseline records
- Escalate complex routing and firewall policy issues with detailed packet capture analysis

### Freelance IT & Web Manager — Self-Employed
**2015 – 2022**

- Designed and implemented network infrastructure for 3 small business client offices
- Configured VLAN segmentation separating employee, guest, and POS terminal traffic
- Deployed and managed UniFi wireless infrastructure across multi-site environments
- Maintained firewall rulesets and performed quarterly security reviews
- Implemented DNS filtering (Pi-hole) for malicious domain blocking across all clients

**Network Projects:**
- **Retail Network Redesign:** Segmented POS terminals into isolated VLAN, eliminating PCI-DSS scope creep risk
- **Office Guest WiFi:** Deployed captive portal with time-limited access and bandwidth throttling
- **Remote Access:** Configured WireGuard VPN for secure admin access, replacing insecure RDP exposure

---

## Network Engineering Projects

### Enterprise Homelab Network — 5-VLAN Segmentation
*Network Engineering | UniFi, pfSense, WireGuard | October 2024*

- Designed and deployed enterprise-grade network with full VLAN segmentation across 5 security zones
- Configured UniFi Dream Machine Pro with stateful firewall and default-deny inter-VLAN policy
- Implemented separate SSIDs per VLAN with WPA3 Enterprise authentication via RADIUS
- Deployed Suricata IPS in inline mode on internet-facing interface for intrusion prevention
- Configured WireGuard VPN with split-tunnel routing for secure remote management access
- Implemented DNSSEC validation and DNS-over-TLS for encrypted DNS resolution

**Network Architecture:**
| VLAN | Purpose | IP Range | Security Policy |
|------|---------|----------|----------------|
| VLAN 10 | Trusted Devices | 10.10.10.0/24 | Full access, monitored |
| VLAN 20 | IoT Devices | 10.10.20.0/24 | Internet only, isolated |
| VLAN 30 | Guest Network | 10.10.30.0/24 | Internet only, rate-limited |
| VLAN 40 | Server Infrastructure | 10.10.40.0/24 | Strict ACL, management access |
| VLAN 50 | DMZ | 10.10.50.0/24 | Inbound allowed, no LAN access |

**Evidence:** [Network Diagrams & Firewall Policy](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/06-homelab/PRJ-HOME-001/assets)

**Key Achievements:**
- Zero cross-VLAN breaches in 12+ months of operation
- IPS blocking 50-100 suspicious connection attempts per day
- Sub-10ms internal DNS resolution with local Pi-hole resolver
- Remote access operational within 30 seconds of VPN connection

---

### Datacenter Virtualization & Core Services
*Datacenter Operations | Proxmox, FreeIPA, Nginx | September 2024*

- Deployed 3-node Proxmox cluster with Ceph storage for high-availability virtual infrastructure
- Configured bonded network interfaces (LACP) for redundant uplinks from each hypervisor node
- Implemented FreeIPA for centralized identity management (DNS, LDAP, Kerberos, SUDO policies)
- Deployed Nginx Proxy Manager as reverse proxy with automatic SSL (Let's Encrypt) for 12 internal services
- Configured Rsyslog centralized logging with structured forwarding to Loki for SIEM-ready log retention

**Infrastructure Details:**
| Component | Technology | Role |
|-----------|------------|------|
| Hypervisors | Proxmox VE 8.x (3 nodes) | VM/container orchestration |
| Storage | Ceph RBD + TrueNAS NFS | Block and file storage |
| Identity | FreeIPA | LDAP, DNS, Kerberos, SUDO |
| Reverse Proxy | Nginx Proxy Manager | SSL termination, routing |
| DNS | Pi-hole + FreeIPA DNS | Ad/malware blocking + internal resolution |
| Logging | Rsyslog → Loki | Centralized log aggregation |

**Evidence:** [Infrastructure Runbooks & Configs](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/06-homelab/PRJ-HOME-002/assets)

---

### Network Monitoring & Observability Stack
*Network Operations | Prometheus, Grafana, SNMP | November 2024*

- Deployed SNMP exporter for network device metrics (UniFi switches, APs, UDM Pro)
- Created Grafana dashboards for network throughput, error rates, and device health
- Configured Alertmanager to notify on interface errors, high utilization, and device unreachability
- Implemented Loki log pipeline capturing Suricata IPS alerts for security event correlation
- Built network capacity planning dashboards tracking bandwidth trends over 90-day windows

**Evidence:** [Monitoring Configuration](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/01-sde-devops/PRJ-SDE-002/assets)

---

## Network Design Principles

### Security-First Architecture

```
Internet
    │
    ▼
[pfSense/UDM Pro] ← Stateful Firewall + IPS
    │
    ├── VLAN 10: Trusted ──→ Full LAN access
    ├── VLAN 20: IoT ──────→ Internet only (isolated)
    ├── VLAN 30: Guest ────→ Internet only (rate-limited)
    ├── VLAN 40: Servers ──→ Strict ACL (mgmt only)
    └── VLAN 50: DMZ ──────→ Inbound allowed, no LAN
```

**Firewall Philosophy:**
- Default deny between all VLANs
- Explicit allow rules with justification comments
- Logging enabled on deny rules for audit trail
- Quarterly firewall policy review and cleanup

---

## Education

**Bachelor of Science in Information Systems**
Colorado State University | 2016 – 2024

**Relevant Coursework:** Network Architecture, TCP/IP Protocols, Network Security, Data Center Operations, Routing & Switching

---

## Certifications & Training

- **CompTIA Network+** *(study in progress)*
- **Cisco CCNA** *(planned 2025 — routing/switching fundamentals)*
- **UniFi Network Associate** *(hands-on experience, certification planned)*
- **CompTIA Security+** *(planned — security hardening context)*

---

## Key Achievements

- **5-VLAN enterprise network:** Designed and deployed complete segmentation from scratch in homelab
- **99.9% network uptime:** Maintained core network services with monitoring and proactive alerting
- **Zero lateral movement:** No cross-VLAN unauthorized access in 12+ months of operation
- **IPS integration:** Suricata blocking 50-100 malicious connection attempts daily
- **Centralized identity:** FreeIPA managing authentication for 10+ services via LDAP/Kerberos

---

## What I Bring to Network Engineering

- **Design Before Deploy:** Document topology and ACL policy before touching hardware
- **Security Mindset:** Every network segment is a potential attack surface — segment accordingly
- **Monitoring-Driven Operations:** If it's not monitored, it doesn't exist operationally
- **Runbook Culture:** Every network change procedure is documented for repeatability
- **Troubleshooting Methodology:** OSI layer-by-layer diagnosis before assuming complex root causes
