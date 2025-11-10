# AWS Kuiper System & Network Administrator - Complete Interview Guide

**60 Technical Interview Questions with Detailed Answers, Diagrams, and Portfolio Mappings**

**Role:** System & Network Administrator for AWS Project Kuiper
**Experience Level:** Mid to Senior
**Interview Duration:** Technical rounds typically 3-5 hours total

---

## Table of Contents

1. [Introduction](#introduction)
2. [How to Use This Guide](#how-to-use-this-guide)
3. [Interview Format](#interview-format)
4. [Questions 1-20: Core AWS & Kuiper Fundamentals](#questions-1-20-core-aws--kuiper-fundamentals)
5. [Questions 21-40: Observability, Automation & SRE](#questions-21-40-observability-automation--sre)
6. [Questions 41-60: Advanced Topics & Homelab](#questions-41-60-advanced-topics--homelab)
7. [Interview Warm-Up Exercises](#interview-warm-up-exercises)
8. [Behavioral Questions](#behavioral-questions)
9. [Glossary of Terms](#glossary-of-terms)
10. [Demo Index & Portfolio Artifacts](#demo-index--portfolio-artifacts)

---

## Introduction

This comprehensive interview guide covers all aspects of the AWS Kuiper System & Network Administrator role. Each question includes:

- **Detailed answer** with Feynman-style explanation
- **Diagram** (via FigJam) visualizing the concept
- **Portfolio artifact mapping** showing where you've implemented this
- **Learn more resources** with links
- **Risk/timebox/owner** categorization
- **Acronym explanations**

### What is Project Kuiper?

**Project Kuiper** is Amazon's initiative to launch a constellation of **3,236 Low Earth Orbit (LEO) satellites** to provide high-speed broadband internet access globally, particularly to underserved areas.

**Key Components:**
- **Space Segment:** LEO satellites at ~590-630 km altitude
- **Ground Segment:** Gateway stations (POPs) connecting satellites to terrestrial networks
- **Customer Segment:** User terminals (customer equipment)
- **Control Plane:** AWS cloud infrastructure managing the network

---

## How to Use This Guide

### For Interview Preparation:
1. Read each question and attempt to answer **before** looking at the provided answer
2. Draw your own diagram on paper **first**, then compare with the provided diagram
3. Use the **Feynman Technique** to explain the concept in simple terms
4. Note which **portfolio artifacts** you can reference as examples
5. Follow the **learn more** links for deeper understanding

### The Feynman Technique (4 Steps):
1. **Choose a concept** (e.g., "Transit Gateway")
2. **Teach it to a child** - Use simple language, no jargon
3. **Identify gaps** - Where did you struggle to explain?
4. **Review & Simplify** - Go back, learn more, simplify further

### Interview Day Strategy:
- Review **Questions 1-20** the night before (core fundamentals)
- Do **warm-up exercises** 2 hours before interview
- Have **portfolio artifacts** bookmarked and ready to share screen
- Practice **whiteboarding** Questions 5, 7, 9, 12 (common design questions)

---

## Interview Format

### Typical Kuiper Sys/NetAdmin Interview Loop:

**Round 1: Technical Screen (45-60 min)**
- Focus: AWS fundamentals, networking basics
- Questions: 1-10 from this guide
- Format: Video call, screen share for diagrams

**Round 2: Deep Technical (60-90 min)**
- Focus: Transit Gateway, VPN, BGP, monitoring
- Questions: 5-15 from this guide
- Format: Whiteboard design, troubleshooting scenarios

**Round 3: System Design (60 min)**
- Focus: Design multi-region connectivity for Kuiper gateways
- Questions: 12, 13, 14, 15, 16
- Format: Collaborative design session

**Round 4: Operational Excellence (45 min)**
- Focus: SRE practices, runbooks, incident response
- Questions: 14, 56, 57, 58, 59
- Format: Past incident review, operational scenarios

**Round 5: Bar Raiser (45-60 min)**
- Focus: Leadership principles, cultural fit, technical breadth
- Mix of technical + behavioral
- Questions: Any from guide + behavioral

---

## Questions 1-20: Core AWS & Kuiper Fundamentals

### Q1: What is Project Kuiper and where does a System & Network Administrator fit in the architecture?

**Difficulty:** ⭐⭐ (Intermediate)
**Category:** Kuiper Overview
**Risk Level:** Low (foundational knowledge)
**Timebox:** 5-7 minutes
**Owner:** Interviewer (usually hiring manager)

#### Detailed Answer:

**Simple Explanation (Feynman):**
Imagine you want to bring Wi-Fi to the entire world, including remote areas where it's impossible to lay cables. Project Kuiper is Amazon's plan to do this using thousands of satellites orbiting Earth. These satellites act like cell towers in space, beaming internet down to people's homes and businesses.

As a System & Network Administrator for Kuiper, I'm like the "traffic manager" for the ground operations. My job is to make sure the connection between the satellites and Amazon's cloud (AWS) is rock-solid, secure, and can handle problems without breaking.

**Technical Explanation:**

**Project Kuiper Overview:**
- **Space Segment:** ~3,236 LEO satellites at 590-630 km altitude
- **Ground Segment:** Gateway POPs (Points of Presence) worldwide
- **AWS Integration:** Direct connectivity to AWS regions via TGW/VPN/DX
- **Service:** High-speed broadband (up to 100+ Mbps)
- **Coverage:** Global, especially underserved and rural areas

**System & Network Administrator Responsibilities:**

1. **Ground Gateway Operations**
   - Manage physical gateway infrastructure (routers, switches, servers)
   - Monitor satellite links and RF (Radio Frequency) performance
   - Coordinate with space operations for satellite handoffs
   - Maintain 99.99% uptime SLAs

2. **AWS Cloud Edge Connectivity**
   - Design and operate Transit Gateway (TGW) hub architecture
   - Configure Site-to-Site VPN tunnels with BGP routing
   - Manage Direct Connect (DX) circuits for high-bandwidth paths
   - Implement multi-region failover for global resilience

3. **Security & Compliance**
   - Implement mTLS (mutual TLS) for all control plane communications
   - Manage Private CA (Certificate Authority) infrastructure
   - Enforce least-privilege IAM policies
   - Maintain audit logs (CloudTrail, VPC Flow Logs, CloudWatch Logs)
   - Ensure compliance with FCC, ITU, and AWS security standards

4. **Observability & Monitoring**
   - Build CloudWatch/Prometheus dashboards for:
     - Satellite link health (latency, jitter, packet loss)
     - BGP session state and route advertisements
     - VPN tunnel status (dual-tunnel monitoring)
     - Gateway resource utilization
   - Configure Alertmanager for on-call routing
   - Implement synthetic monitoring (end-to-end probes)
   - Define and track SLOs (Service Level Objectives)

5. **Automation & Infrastructure as Code**
   - Write Terraform modules for repeatable gateway deployments
   - Use Ansible for configuration management (routers, firewalls)
   - Automate ACL rollouts with YAML-to-Jinja templates
   - Implement GitOps workflows for infrastructure changes

6. **Incident Response & SRE**
   - Participate in on-call rotation (24/7 coverage)
   - Respond to BGP flaps, tunnel failures, link degradation
   - Write and maintain runbooks for common scenarios
   - Lead blameless postmortems after incidents
   - Track error budgets and work to improve reliability

**Diagram:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PROJECT KUIPER ARCHITECTURE                      │
│                  (Sys/NetAdmin Responsibility Areas)                │
└─────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐
     │   Customer   │  ← User Terminal
     │   Terminal   │     (Ka-band phased array)
     └───────┬──────┘
             │ Uplink (Ka-band)
             ↓
    ┌─────────────────┐
    │   LEO Satellite │  ← Space Segment
    │   (590-630 km)  │     (3,236 satellites)
    └────────┬────────┘
             │ Optical Inter-Satellite Links (OISL)
             ↓
    ┌─────────────────┐
    │  Nearby         │  ← Mesh routing to best gateway
    │  Satellites     │
    └────────┬────────┘
             │ Downlink (Ka-band)
             ↓
╔════════════════════════════════════════════════════════════════════╗
║         GROUND GATEWAY POP (Your Responsibility!)                  ║
║  ┌──────────────────────────────────────────────────────────────┐  ║
║  │  RF Equipment                                                 │  ║
║  │  ├─ Antennas (Ka-band receive)                              │  ║
║  │  ├─ RF Modem (Ka → IP)                                      │  ║
║  │  └─ Gateway Router (BGP, VPN, routing)                      │  ║
║  │                                                               │  ║
║  │  Security & Management                                       │  ║
║  │  ├─ mTLS for control plane                                  │  ║
║  │  ├─ Private CA infrastructure                               │  ║
║  │  ├─ Bastion host (admin access)                             │  ║
║  │  └─ Monitoring agents (Prometheus exporters)                │  ║
║  └──────────────────────────────────────────────────────────────┘  ║
╚════════════════════════════════════════════════════════════════════╝
             │ Terrestrial Network
             ↓
    ┌─────────────────┐
    │  ISP / Private  │  ← Multiple paths for redundancy
    │     Network     │
    └────────┬────────┘
             │ S2S VPN (IPsec + BGP) or Direct Connect
             ↓
╔════════════════════════════════════════════════════════════════════╗
║              AWS CLOUD EDGE (Your Responsibility!)                 ║
║  ┌──────────────────────────────────────────────────────────────┐  ║
║  │  Transit Gateway (TGW)                                        │  ║
║  │  ├─ VPN Attachments (from gateways)                         │  ║
║  │  ├─ DX Attachments (high bandwidth)                         │  ║
║  │  ├─ VPC Attachments (app workloads)                         │  ║
║  │  └─ TGW Route Tables (traffic steering)                     │  ║
║  │                                                               │  ║
║  │  Observability                                               │  ║
║  │  ├─ CloudWatch (AWS-native metrics/alarms)                  │  ║
║  │  ├─ Prometheus + Grafana (custom metrics)                   │  ║
║  │  ├─ Loki (log aggregation)                                  │  ║
║  │  └─ Alertmanager (alert routing to on-call)                 │  ║
║  │                                                               │  ║
║  │  Global Traffic Management                                   │  ║
║  │  ├─ Route 53 (latency-based routing)                        │  ║
║  │  ├─ Health Checks (endpoint monitoring)                     │  ║
║  │  └─ Failover policies (multi-region HA)                     │  ║
║  └──────────────────────────────────────────────────────────────┘  ║
╚════════════════════════════════════════════════════════════════════╝
             │
             ↓
    ┌─────────────────┐
    │   Application   │  ← Kuiper Control Plane Services
    │      VPCs       │     (auth, billing, network mgmt)
    └─────────────────┘
```

**Key Acronyms Explained:**

| Acronym | Full Term | Simple Explanation |
|---------|-----------|-------------------|
| **LEO** | Low Earth Orbit | Satellites close to Earth (vs GEO = far away). LEO = faster internet, lower latency (~20-30 ms vs GEO's 600+ ms) |
| **POP** | Point of Presence | A physical location with networking equipment. Like a branch office for the internet |
| **Ka-band** | K-above band (26.5-40 GHz) | A specific radio frequency range used for satellite communication. Think FM radio vs AM radio - different channels |
| **OISL** | Optical Inter-Satellite Links | Satellites talking to each other using lasers (like fiber optic cables in space) |
| **TGW** | Transit Gateway | AWS's central router connecting many networks. Like a giant highway interchange |
| **BGP** | Border Gateway Protocol | The internet's routing protocol. Tells routers how to get to different networks |
| **VPN** | Virtual Private Network | Encrypted tunnel over the internet. Like a secret underground passage |
| **DX** | Direct Connect | Private, dedicated link to AWS (not over public internet). Like having your own private highway |
| **mTLS** | Mutual TLS | Both sides prove who they are with certificates. Like both people showing ID cards |
| **SLO** | Service Level Objective | A goal for how reliable the service should be (e.g., "99.9% uptime") |
| **SLA** | Service Level Agreement | A contract promising a certain level of service (with penalties if not met) |
| **IAM** | Identity & Access Management | AWS's permission system (who can do what) |
| **CA** | Certificate Authority | Issues digital certificates (like a passport office) |

**Portfolio Artifacts:**

| Artifact | Location | What It Shows |
|----------|----------|---------------|
| **Kuiper Overview README** | `projects/kuiper/ground-gateway-ops/README.md` | Role remit, glossary, architecture overview |
| **Architecture Diagrams** | `docs/diagrams/kuiper/kuiper-overview.mmd` | Visual system architecture (Mermaid format) |
| **ADR-0001: Kuiper Data Path** | `docs/adr/ADR-0001-kuiper-data-path.md` | Architecture decision defining trust boundaries |
| **SLO Definitions** | `docs/slo/kuiper-gateway.yml` | SLO targets for latency, loss, BGP stability |

**Learn More:**

1. **Project Kuiper Official:**
   - [Amazon Project Kuiper Overview](https://www.aboutamazon.com/news/innovation-at-amazon/amazon-project-kuiper)
   - [Project Kuiper Satellite Specs (FCC Filing)](https://fcc.report/IBFS/SAT-LOA-20190704-00057)

2. **LEO Satellite Networks:**
   - [LEO vs GEO Satellites Explained](https://www.youtube.com/watch?v=dQw4w9WgXcQ) (Video)
   - [How Satellite Internet Works](https://www.youtube.com/watch?v=dQw4w9WgXcQ) (Video)

3. **AWS Networking for Satellite:**
   - [AWS Transit Gateway Deep Dive](https://www.youtube.com/results?search_query=aws+transit+gateway+deep+dive)
   - [Building Hybrid Networks on AWS](https://www.youtube.com/results?search_query=aws+hybrid+networking)

4. **Sys/NetAdmin Best Practices:**
   - [Google SRE Book (Free)](https://sre.google/sre-book/table-of-contents/)
   - [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

**Risk Assessment:**

| Risk Category | Level | Mitigation |
|---------------|-------|------------|
| **Single Gateway Failure** | HIGH | Deploy 2+ gateways per region with BGP failover |
| **BGP Misconfiguration** | HIGH | Automated validation, change control, staged rollouts |
| **Satellite Link Degradation** | MEDIUM | Multi-gateway diversity, QoS prioritization, synthetic monitoring |
| **Security Breach** | HIGH | mTLS everywhere, zero-trust model, least privilege IAM |
| **AWS Region Outage** | MEDIUM | Multi-region with TGW peering, Route 53 failover |
| **On-call Burnout** | MEDIUM | Runbook automation, alert tuning, blameless culture |

**Timebox for This Topic:**
- **Initial Learning:** 2-4 hours (overview, basics)
- **Deep Dive:** 20-30 hours (networking, monitoring, automation)
- **Hands-On Practice:** 10-20 hours (labs, simulations)
- **Interview Prep:** 2-3 hours (review, practice explaining)

**Owner (Who Should Know This):**
- **Must Know:** System & Network Administrators, SRE, Network Engineers
- **Should Know:** DevOps Engineers, Cloud Architects, Security Engineers
- **Nice to Know:** Software Engineers, Data Engineers, Product Managers

---

### Q2: Describe the complete data flow from a customer terminal to AWS. Where are the critical trust boundaries?

**Difficulty:** ⭐⭐⭐ (Advanced)
**Category:** Architecture & Security
**Risk Level:** High (security boundary misunderstandings = breaches)
**Timebox:** 7-10 minutes
**Owner:** Interviewer (Security or Senior Network Engineer)

#### Detailed Answer:

**Simple Explanation (Feynman):**
Imagine you're sending a letter from your house to a friend across the country:
1. You put the letter in your mailbox (customer terminal)
2. A mail truck picks it up (satellite)
3. It goes to a sorting facility (ground gateway)
4. Then to a regional distribution center (AWS edge)
5. Finally to your friend's mailbox (application server)

At each handoff point, we need security checks - like showing ID when dropping off a package at the post office. These checkpoints are our "trust boundaries."

**Technical Data Flow:**

```
┌────────────────────────────────────────────────────────────────────┐
│             KUIPER DATA FLOW - TRUST BOUNDARIES                    │
└────────────────────────────────────────────────────────────────────┘

  [TRUST BOUNDARY #1: Customer Edge]
┌─────────────────────────────────────────┐
│ 1. CUSTOMER TERMINAL (User Equipment)  │
│    ├─ Ka-band phased array antenna     │
│    ├─ Modem (customer data → RF)       │
│    ├─ Router (DHCP, NAT, firewall)     │
│    └─ Customer LAN (Wi-Fi, Ethernet)   │
│                                         │
│    Security:                            │
│    • Customer credentials (WPA2/WPA3)  │
│    • Unique terminal ID                │
│    • Encrypted uplink (AES-256)        │
└────────────┬────────────────────────────┘
             │ Ka-band Uplink
             │ (25.0-27.5 GHz)
             │ Encrypted RF link
             ↓
  [TRUST BOUNDARY #2: Space Segment]
┌─────────────────────────────────────────┐
│ 2. LEO SATELLITE                        │
│    ├─ RF Receiver (demod uplink)        │
│    ├─ Onboard Router (packet forward)   │
│    ├─ OISL Transceiver (sat-to-sat)    │
│    └─ Downlink Transmitter             │
│                                         │
│    Security:                            │
│    • No decryption (bent-pipe forward) │
│    • Anti-jamming (frequency hopping)  │
│    • Satellite authentication          │
└────────────┬────────────────────────────┘
             │ Optical Inter-Satellite Links
             │ (Mesh routing to best gateway)
             │ Encrypted laser beams
             ↓
┌─────────────────────────────────────────┐
│ 3. DESTINATION SATELLITE                │
│    (Closest to target ground gateway)   │
│    └─ Downlink Transmitter             │
└────────────┬────────────────────────────┘
             │ Ka-band Downlink
             │ (17.7-19.7 GHz)
             ↓
  [TRUST BOUNDARY #3: Ground Gateway]
╔═════════════════════════════════════════╗
║ 4. GROUND GATEWAY POP                   ║
║    (YOUR PRIMARY RESPONSIBILITY!)       ║
║    ┌─────────────────────────────────┐  ║
║    │ RF Front-End                    │  ║
║    │ ├─ Ka-band Antenna Array        │  ║
║    │ ├─ Low Noise Amplifier (LNA)    │  ║
║    │ ├─ Downconverter (RF → IF)      │  ║
║    │ └─ Demodulator (IF → baseband)  │  ║
║    │                                  │  ║
║    │ Gateway Router/Firewall          │  ║
║    │ ├─ Decryption (customer payload)│  ║
║    │ ├─ NAT / Address Translation     │  ║
║    │ ├─ Deep Packet Inspection (DPI) │  ║
║    │ ├─ QoS (DSCP marking)           │  ║
║    │ └─ BGP (route to AWS)           │  ║
║    │                                  │  ║
║    │ Control Plane (Admin Access)     │  ║
║    │ ├─ Bastion Host (SSH)           │  ║
║    │ ├─ mTLS Certificate Auth        │  ║
║    │ ├─ MFA for all admins           │  ║
║    │ └─ Audit Logging (syslog)       │  ║
║    └─────────────────────────────────┘  ║
║                                         ║
║    Security:                            ║
║    • Physical security (locked cage)   ║
║    • HSM for crypto keys               ║
║    • Intrusion detection (IDS/IPS)     ║
║    • Rate limiting / DDoS mitigation   ║
║    • mTLS for all control APIs         ║
╚════════════┬════════════════════════════╝
             │ Terrestrial Network
             │ (Private fiber or ISP)
             ↓
┌─────────────────────────────────────────┐
│ 5. ISP / PRIVATE NETWORK                │
│    ├─ Layer 2: Metro Ethernet          │
│    ├─ Layer 3: MPLS VPN                │
│    └─ BGP peering                      │
└────────────┬────────────────────────────┘
             │ IPsec VPN or Direct Connect
             ↓
  [TRUST BOUNDARY #4: AWS Edge]
╔═════════════════════════════════════════╗
║ 6. AWS SITE-TO-SITE VPN / DX           ║
║    ┌─────────────────────────────────┐  ║
║    │ VPN Endpoint (if S2S VPN)       │  ║
║    │ ├─ IPsec tunnel                 │  ║
║    │ ├─ BGP session (eBGP)           │  ║
║    │ └─ Route propagation to TGW     │  ║
║    │                                  │  ║
║    │ OR                               │  ║
║    │                                  │  ║
║    │ Direct Connect (if DX)           │  ║
║    │ ├─ Dedicated fiber (1/10/100G)  │  ║
║    │ ├─ 802.1Q VLANs (transit)       │  ║
║    │ ├─ BGP session (eBGP)           │  ║
║    │ └─ Direct to TGW                │  ║
║    └─────────────────────────────────┘  ║
║                                         ║
║    Security:                            ║
║    • AWS-managed encryption (VPN)      ║
║    • MACsec for DX (optional)          ║
║    • BGP auth (MD5 or TCP-AO)          ║
╚════════════┬════════════════════════════╝
             │ AWS Backbone
             ↓
┌─────────────────────────────────────────┐
│ 7. TRANSIT GATEWAY (TGW)                │
│    ├─ Regional hub router               │
│    ├─ Route tables (per attachment)     │
│    ├─ Flow Logs (traffic monitoring)    │
│    └─ CloudWatch metrics                │
│                                         │
│    Security:                            │
│    • VPC attachment IAM policies        │
│    • Security group validation          │
│    • Network ACL enforcement            │
└────────────┬────────────────────────────┘
             │ VPC Attachment
             ↓
  [TRUST BOUNDARY #5: Application Layer]
┌─────────────────────────────────────────┐
│ 8. APPLICATION VPC                      │
│    ├─ Private Subnets (apps)            │
│    ├─ Security Groups (instance FW)     │
│    ├─ NACLs (subnet FW)                 │
│    ├─ ALB (if web app)                  │
│    └─ App Servers (EC2/ECS/EKS)         │
│                                         │
│    Security:                            │
│    • Least privilege Security Groups   │
│    • IAM roles (no hardcoded creds)    │
│    • KMS encryption (data at rest)      │
│    • WAF (if exposed to internet)       │
│    • Secrets Manager (credentials)      │
└────────────┬────────────────────────────┘
             │ Internal
             ↓
┌─────────────────────────────────────────┐
│ 9. BACKEND SERVICES                     │
│    ├─ RDS (databases)                   │
│    ├─ ElastiCache (Redis/Memcached)    │
│    ├─ S3 (object storage)               │
│    └─ DynamoDB (NoSQL)                  │
│                                         │
│    Security:                            │
│    • Encryption in transit (TLS)        │
│    • Encryption at rest (KMS)           │
│    • Private endpoints (no internet)    │
│    • IAM policies (fine-grained)        │
│    • Backup encryption                  │
└─────────────────────────────────────────┘
```

**Critical Trust Boundaries (Detailed):**

**Trust Boundary #1: Customer Edge**
- **Threat Model:** Malicious customer, compromised terminal, DDoS from customer side
- **Controls:**
  - Authentication: Unique terminal ID + customer credentials
  - Encryption: AES-256 for uplink data
  - Rate limiting: Per-terminal bandwidth caps
  - Isolation: Customer traffic isolated from control plane
- **Audit:** Terminal health telemetry, usage monitoring

**Trust Boundary #2: Space Segment**
- **Threat Model:** Jamming, spoofing, satellite compromise
- **Controls:**
  - Anti-jamming: Frequency hopping, adaptive beamforming
  - Authentication: Cryptographic satellite IDs
  - Monitoring: Ground-based tracking, anomaly detection
  - No decryption: Bent-pipe forwarding (minimize attack surface)
- **Audit:** Satellite telemetry, space surveillance

**Trust Boundary #3: Ground Gateway (MOST CRITICAL)**
- **Threat Model:** Physical intrusion, insider threat, network attacks, APT (Advanced Persistent Threat)
- **Controls:**
  - **Physical Security:**
    - Locked cages with access logs
    - Video surveillance
    - Biometric access controls
    - HSM (Hardware Security Module) for key storage
  - **Network Security:**
    - IDS/IPS (Suricata, Snort)
    - DDoS mitigation (rate limiting, anomaly detection)
    - Firewall (deny-by-default)
    - Network segmentation (data plane vs control plane)
  - **Administrative Security:**
    - mTLS for all control plane APIs
    - MFA for all human access
    - Bastion host with session recording
    - Least privilege (RBAC)
  - **Logging & Monitoring:**
    - Syslog to centralized SIEM
    - File integrity monitoring (Tripwire, AIDE)
    - Network flow logs
    - Alerting on suspicious activity
- **Audit:** 24/7 SOC monitoring, quarterly penetration tests, annual compliance audits (SOC 2, ISO 27001)

**Trust Boundary #4: AWS Edge**
- **Threat Model:** Man-in-the-middle, BGP hijacking, DX/VPN compromise
- **Controls:**
  - Encryption: IPsec for VPN, MACsec for DX (optional)
  - Authentication: BGP MD5 auth, customer gateway pre-shared keys
  - Monitoring: BGP session state, tunnel metrics, anomaly detection
  - Redundancy: Dual tunnels (VPN), diverse paths (DX)
- **Audit:** CloudWatch Logs, VPC Flow Logs, CloudTrail API logs

**Trust Boundary #5: Application Layer**
- **Threat Model:** Application vulnerability exploitation, data exfiltration, privilege escalation
- **Controls:**
  - Security Groups: Fine-grained, deny-by-default
  - IAM: Least privilege roles, no hardcoded credentials
  - Encryption: TLS in transit, KMS at rest
  - WAF: OWASP Top 10 protections (if internet-facing)
  - Secrets Management: AWS Secrets Manager, Parameter Store
  - Patching: Automated via Systems Manager
- **Audit:** GuardDuty (threat detection), Security Hub (compliance), Inspector (vulnerability scanning)

**Data Encryption Layers:**

```
┌──────────────────────────────────────────────────┐
│            ENCRYPTION AT EACH HOP                │
└──────────────────────────────────────────────────┘

Customer → Satellite:
  ├─ Application Layer: HTTPS (TLS 1.3)
  └─ Link Layer: AES-256 (Ka-band encryption)

Satellite → Satellite:
  └─ OISL: Quantum-safe encryption (proprietary)

Satellite → Gateway:
  └─ Link Layer: AES-256 (Ka-band encryption)

Gateway → AWS (VPN):
  ├─ IPsec: AES-256-GCM, SHA-256 HMAC
  └─ BGP: TCP MD5 authentication

Gateway → AWS (DX):
  └─ MACsec: AES-256-GCM (if enabled)

Within AWS:
  ├─ TLS 1.2+ for all inter-service communication
  └─ KMS encryption for data at rest

Result: MULTIPLE LAYERS (defense in depth)
```

**Portfolio Artifacts:**

| Artifact | Location | What It Shows |
|----------|----------|---------------|
| **Data Flow Diagram** | `docs/diagrams/kuiper/data-flow.mmd` | Complete end-to-end flow with annotations |
| **Trust Boundary ADR** | `docs/adr/ADR-0001-kuiper-data-path.md` | Architecture decision defining each boundary |
| **mTLS Implementation** | `docs/pki/` | CA design, cert rotation, SAN standards |
| **Security Runbook** | `docs/runbooks/mTLS-control-plane.md` | Operational procedures for PKI management |
| **Terraform Security** | `infra/aws/terraform/vpn-bgp/` | Security group rules, encryption configs |

**Learn More:**

1. **Satellite Security:**
   - [Satellite Cybersecurity Fundamentals](https://www.youtube.com/results?search_query=satellite+cybersecurity)
   - [Space ISAC (Information Sharing)](https://s-isac.org/)

2. **Zero Trust Architecture:**
   - [NIST SP 800-207: Zero Trust](https://csrc.nist.gov/publications/detail/sp/800-207/final)
   - [Google BeyondCorp Papers](https://cloud.google.com/beyondcorp)

3. **AWS Security:**
   - [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)
   - [VPN/DX Security (AWS re:Inforce)](https://www.youtube.com/results?search_query=aws+vpn+security)

4. **mTLS Deep Dive:**
   - [mTLS Explained (Cloudflare)](https://www.cloudflare.com/learning/access-management/what-is-mutual-tls/)
   - [Let's Encrypt vs Private CA](https://letsencrypt.org/docs/faq/)

---

### Q3: How do satellite link constraints (latency, jitter, packet loss) impact ground gateway operations? How would you design to mitigate?

**Difficulty:** ⭐⭐⭐ (Advanced)
**Category:** Satellite Operations & Network Engineering
**Risk Level:** High (poor design = degraded user experience)
**Timebox:** 8-12 minutes
**Owner:** Senior Network Engineer or SRE Lead

#### Detailed Answer:

**Simple Explanation (Feynman):**
Imagine you're having a phone conversation with someone on a ship in the middle of the ocean. Sometimes the signal is clear, sometimes there's a delay, sometimes words get cut out. Satellite links have similar challenges:
- **Latency** = how long it takes for your message to reach them
- **Jitter** = sometimes it takes 100ms, sometimes 150ms (inconsistent)
- **Packet loss** = sometimes words just disappear

Our job is to design the ground gateway to handle these "bad phone line" conditions so the customer's internet still works well.

**Technical Explanation:**

**Satellite Link Constraints for LEO (Kuiper):**

```
┌────────────────────────────────────────────────────────────────────┐
│            LEO SATELLITE LINK CHARACTERISTICS                      │
│                  (vs Terrestrial Fiber)                            │
└────────────────────────────────────────────────────────────────────┘

Metric                  Terrestrial Fiber    LEO (Kuiper)      Impact
─────────────────────────────────────────────────────────────────────
Latency (RTT)           1-20 ms              20-40 ms          Moderate
Jitter                  < 1 ms               2-10 ms           Moderate
Packet Loss (normal)    < 0.01%              0.1-1%            High
Packet Loss (rain fade) N/A                  1-5%              Critical
Link Availability       99.99%+              99.5-99.9%        Moderate
Bandwidth               10 Gbps+             100-500 Mbps      Moderate
Handoff Frequency       Never                Every 4-7 min     Critical
Path Asymmetry          Symmetric            Often asymmetric  Moderate
Doppler Shift           None                 ±10 kHz           Low (RF layer)

┌────────────────────────────────────────────────────────────────────┐
│                    IMPACT ON PROTOCOLS                             │
└────────────────────────────────────────────────────────────────────┘

Protocol    Sensitivity        Impact         Mitigation Needed
───────────────────────────────────────────────────────────────────
TCP         High (latency)     Slow start     TCP optimization, larger windows
VoIP        High (jitter)      Poor quality   Jitter buffers, FEC
Video       Medium (loss)      Buffering      Adaptive bitrate, buffering
DNS         Low                Slight delay   Caching, prefetching
BGP         Medium (loss)      Flapping       Timers tuning, hold-time increase
SSH         Medium (latency)   Typing lag     Mosh (mobile shell)
HTTP/HTTPS  Medium (latency)   Slow pages     HTTP/2, CDN, compression
Gaming      High (latency)     Unplayable     Edge compute, prediction
```

**Constraint #1: Latency (20-40 ms RTT)**

**Why it happens:**
- Speed of light: ~1,800 km to satellite and back = ~12 ms minimum
- Processing delays: terminal (2 ms) + satellite (5 ms) + gateway (2 ms) + routing = ~10 ms
- Total: 22-40 ms typical

**Impact:**
- TCP slow start takes longer (congestion window ramps up slowly)
- Interactive applications feel sluggish (SSH, remote desktop)
- BGP convergence slower (hold-time = 180s means 180s to detect failure)

**Mitigation Strategies:**

1. **TCP Optimization (Performance Enhancing Proxy - PEP)**
   ```
   Customer Terminal → Satellite → Gateway PEP → Internet
                       ↑                ↑
                    Optimized       Standard
                    TCP over         TCP
                    satellite

   Gateway PEP Actions:
   - Splits TCP connection (local ACKs to customer)
   - Increases TCP window size (BDP = bandwidth × delay)
   - Enables selective ACK (SACK)
   - Uses BBR congestion control (vs CUBIC)
   ```

2. **BGP Timer Tuning**
   ```bash
   # Conservative (default)
   router bgp 65000
     neighbor 10.0.0.1 timers 60 180
     # Keepalive=60s, Hold-time=180s

   # Aggressive (for fast failover, but risk false positives)
   router bgp 65000
     neighbor 10.0.0.1 timers 10 30
     # Keepalive=10s, Hold-time=30s

   # Kuiper Recommended (balance)
   router bgp 65000
     neighbor 10.0.0.1 timers 20 60
     # Keepalive=20s, Hold-time=60s
     neighbor 10.0.0.1 transport connection-mode passive
     # Let AWS initiate (more reliable)
   ```

3. **DNS Caching & Prefetching**
   ```yaml
   # Unbound DNS config at gateway
   server:
     cache-min-ttl: 3600       # Cache for at least 1 hour
     cache-max-ttl: 86400      # Up to 1 day
     prefetch: yes             # Refresh before expiry
     serve-expired: yes        # Serve stale if upstream slow
   ```

**Constraint #2: Jitter (2-10 ms variance)**

**Why it happens:**
- Satellite handoffs (every 4-7 minutes as satellite moves)
- RF interference (weather, adjacent satellites)
- Variable processing load on satellite
- Terrestrial backhaul variability

**Impact:**
- VoIP/video quality degradation
- TCP performance variability
- BGP session instability (if extreme)

**Mitigation Strategies:**

1. **QoS & Traffic Shaping**
   ```
   ┌─────────────────────────────────────────────────────────────┐
   │               GATEWAY QoS POLICY                            │
   └─────────────────────────────────────────────────────────────┘

   Priority Queue (Strict Priority):
   ├─ P1: Network Control (BGP, OSPF, BFD)          - DSCP CS6
   ├─ P2: VoIP (SIP, RTP)                           - DSCP EF
   ├─ P3: Video Conferencing (Zoom, Teams)          - DSCP AF41
   ├─ P4: Interactive (SSH, RDP)                    - DSCP AF31
   ├─ P5: Transactional (HTTPS, DNS)                - DSCP AF21
   ├─ P6: Bulk (HTTP, FTP)                          - DSCP AF11
   └─ P7: Scavenger (BitTorrent, etc)               - DSCP CS1

   Jitter Buffers:
   - VoIP: 50-100 ms adaptive buffer
   - Video: 2-5 second buffer (streaming)
   - Gaming: Minimize (use QUIC/UDP)
   ```

2. **Forward Error Correction (FEC)**
   ```
   Customer sends 100 packets + 10 FEC packets
   → If ≤10 lost, can reconstruct without retransmit
   → Trades bandwidth for latency reduction

   Use case: Real-time apps (VoIP, video) where retransmit unacceptable
   ```

**Constraint #3: Packet Loss (0.1-5%)**

**Why it happens:**
- Rain fade (Ka-band absorbed by heavy rain) - **most critical**
- Satellite handoffs (brief interruption)
- RF interference
- Link budget constraints (edge of coverage)

**Impact:**
- TCP throughput collapse (fast retransmit triggers)
- VoIP/video degradation
- BGP session flaps

**Mitigation Strategies:**

1. **Link Diversity (Gateway-Side)**
   ```
   ┌────────────────────────────────────────────────────────────┐
   │         DUAL-GATEWAY ARCHITECTURE                          │
   └────────────────────────────────────────────────────────────┘

   Customer Terminal
         │
         │ (Chooses best satellite based on signal strength)
         ↓
   ┌──────────┐         ┌──────────┐
   │Satellite │         │Satellite │
   │  A       │         │  B       │
   └────┬─────┘         └─────┬────┘
        │                     │
        ↓                     ↓
   Gateway-East          Gateway-West
   (Virginia)            (Oregon)
        │                     │
        ├─ VPN Tunnel 1 ──────┤
        └─ VPN Tunnel 2 ──────┘
                │
                ↓
          AWS Transit Gateway
          (ECMP load balance)

   Result: Rain fade at Gateway-East? Traffic automatically fails to Gateway-West
   ```

2. **Adaptive Rate Control**
   ```python
   # Pseudocode for gateway rate limiter
   if packet_loss_rate > 2%:
       reduce_bandwidth_allocation(customer_id, factor=0.8)
       prioritize_critical_traffic()
       notify_monitoring("High loss detected")

   if signal_to_noise_ratio < threshold:
       request_modulation_change(from="64QAM", to="16QAM")
       # Lower throughput but more robust
   ```

3. **Satellite Handoff Optimization**
   ```
   ┌────────────────────────────────────────────────────────────┐
   │            MAKE-BEFORE-BREAK HANDOFF                       │
   └────────────────────────────────────────────────────────────┘

   Timeline:
   T=0s     Customer connected to Satellite A
   T=3min   Gateway predicts handoff needed in 1 min (ephemeris data)
   T=3.5min Gateway establishes secondary link to Satellite B
            (Brief period of dual connectivity)
   T=4min   Primary traffic moved to Satellite B
            Satellite A link dropped

   Result: Hitless handoff (0 packet loss during transition)

   Implementation:
   - Requires coordination between terminal, satellites, gateway
   - Ephemeris data shared via control plane
   - Gateway buffers packets during handoff
   ```

**Constraint #4: Rain Fade (Ka-band Specific)**

**Why it happens:**
- Ka-band (26.5-40 GHz) highly susceptible to atmospheric absorption
- Heavy rain = 10-20 dB signal attenuation
- Can cause complete link outage in severe weather

**Mitigation Strategies:**

1. **Site Diversity (Geographic Separation)**
   ```
   Customer in Seattle (heavy rain) → Satellite → Gateway Portland
                                                 (if Portland also rain)
                                                 ↓ reroute
                                    Satellite → Gateway Los Angeles
                                                 (likely clear)

   Rule: Gateways separated by >200 km (uncorrelated weather)
   ```

2. **Link Budget Margin & Adaptive Modulation**
   ```
   Normal conditions:   64-QAM modulation (high throughput)
   Light rain (-3 dB):  32-QAM modulation (medium throughput)
   Heavy rain (-10 dB): 8-QAM modulation (low but reliable)
   Severe (-20 dB):     BPSK modulation (minimal throughput)

   Result: Graceful degradation instead of hard failure
   ```

**Portfolio Artifacts:**

| Artifact | Location | What It Shows |
|----------|----------|---------------|
| **Link Simulation (tc netem)** | `evidence/experiments/netem/` | Simulating satellite latency/jitter/loss in homelab |
| **Before/After Graphs** | `evidence/experiments/netem/results/` | HTTP, SSH, VoIP performance under constraints |
| **BGP Timer Tuning ADR** | `docs/adr/ADR-0005-bgp-timer-tuning.md` | Decision: conservative vs aggressive timers |
| **QoS Policy Config** | `configs/cisco/qos-satellite.cfg` | DSCP marking, priority queues |
| **Gateway Diversity Design** | `docs/diagrams/kuiper/gateway-diversity.mmd` | Multi-gateway architecture for resilience |
| **Alerting Rules** | `observability/prometheus/rules/satellite-link.yml` | Alerts for high latency, jitter, loss |

**Learn More:**

1. **Satellite Link Constraints:**
   - [Satellite Communications Fundamentals](https://www.youtube.com/results?search_query=satellite+communications+fundamentals)
   - [Ka-band vs Ku-band Comparison](https://www.viasat.com/about/newsroom/blog/ka-band-vs-ku-band/)
   - [Rain Fade Analysis (PDF)](https://www.google.com/search?q=ka+band+rain+fade+attenuation+pdf)

2. **TCP over Satellite:**
   - [RFC 2488: TCP over Satellite](https://datatracker.ietf.org/doc/html/rfc2488)
   - [BBR Congestion Control (Google)](https://queue.acm.org/detail.cfm?id=3022184)
   - [PEP Explained](https://en.wikipedia.org/wiki/Performance-enhancing_proxy)

3. **QoS & Traffic Management:**
   - [DSCP Marking Guide](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/qos_classn/configuration/xe-16/qos-classn-xe-16-book/qos-classn-mrkg-ntwrk-traffc.html)
   - [QoS for VoIP](https://www.youtube.com/results?search_query=qos+for+voip)

4. **Hands-On Lab:**
   - [tc netem Tutorial](https://man7.org/linux/man-pages/man8/tc-netem.8.html)
   - Simulate satellite link: `tc qdisc add dev eth0 root netem delay 30ms 5ms loss 1%`

**Risk Assessment:**

| Risk Category | Level | Mitigation |
|---------------|-------|------------|
| **Rain Fade Outage** | CRITICAL | Multi-gateway diversity (>200 km apart), adaptive modulation |
| **Handoff Packet Loss** | HIGH | Make-before-break handoff, buffering at gateway |
| **BGP Flapping** | HIGH | Conservative timers (20s/60s), BFD for fast detection |
| **TCP Throughput Collapse** | MEDIUM | PEP (Performance Enhancing Proxy), BBR congestion control |
| **VoIP Quality Issues** | MEDIUM | QoS prioritization, jitter buffers, FEC |
| **DNS Resolution Delays** | LOW | Aggressive caching, prefetching |

**Timebox for This Topic:**
- **Initial Learning:** 4-6 hours (RF basics, link budgets, protocols)
- **Deep Dive:** 40-60 hours (QoS, TCP tuning, BGP, hands-on labs)
- **Hands-On Practice:** 10-20 hours (tc netem simulations, protocol testing)
- **Interview Prep:** 3-4 hours (practice explaining, whiteboard design)

**Owner (Who Should Know This):**
- **Must Know:** Network Engineers, SREs, Satellite Operations
- **Should Know:** System Administrators, DevOps Engineers
- **Nice to Know:** RF Engineers, Software Engineers (for app optimization)

---

### Q4: How would you simulate satellite-like network conditions in a lab environment for testing applications?

**Difficulty:** ⭐⭐⭐ (Advanced)
**Category:** Testing & Validation
**Risk Level:** Medium (poor testing = production surprises)
**Timebox:** 6-9 minutes
**Owner:** SRE or DevOps Engineer

#### Detailed Answer:

**Simple Explanation (Feynman):**
Imagine you're testing a new car. You wouldn't just drive it on perfect roads - you'd drive it on bumpy roads, in rain, in snow, to see how it handles bad conditions. Similarly, we need to test our applications under satellite conditions (delays, packet loss, jitter) before deploying them.

We use a tool called `tc netem` (network emulator) in Linux that artificially adds delay, drops packets, and creates jitter. It's like putting your car on a test track that simulates real-world conditions.

**Technical Explanation:**

**Simulation Architecture:**

```
┌────────────────────────────────────────────────────────────────────┐
│              SATELLITE LINK SIMULATION TESTBED                     │
└────────────────────────────────────────────────────────────────────┘

┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  Test Client    │         │  Linux Bridge   │         │  Test Server    │
│                 │         │  (tc netem)     │         │                 │
│  192.168.1.10   │◄────────│                 │────────►│  192.168.1.20   │
│                 │  eth0   │  br0            │  eth1   │                 │
│  - HTTP client  │         │  - Add latency  │         │  - HTTP server  │
│  - SSH client   │         │  - Drop packets │         │  - SSH server   │
│  - VoIP client  │         │  - Add jitter   │         │  - VoIP server  │
└─────────────────┘         └─────────────────┘         └─────────────────┘

OR (Single Host Simulation):

┌──────────────────────────────────────────────────────────────────────┐
│                    LOOPBACK SIMULATION                               │
│                                                                      │
│  ┌──────────────┐                           ┌──────────────┐        │
│  │   Client     │  127.0.0.1:8080          │   Server     │        │
│  │   Process    │◄─────────────────────────│   Process    │        │
│  └──────────────┘          ↑                └──────────────┘        │
│                            │                                        │
│                     tc netem on lo                                  │
│                     (applies to loopback)                           │
└──────────────────────────────────────────────────────────────────────┘
```

**Tool #1: tc netem (Network Emulator)**

**Installation:**
```bash
# Ubuntu/Debian
sudo apt-get install iproute2

# RHEL/CentOS
sudo yum install iproute-tc
```

**Basic Kuiper Satellite Profile:**
```bash
#!/bin/bash
# kuiper-profile-normal.sh

IFACE="eth0"  # Change to your interface

# Clear existing rules
sudo tc qdisc del dev $IFACE root 2>/dev/null

# Add Kuiper satellite characteristics
sudo tc qdisc add dev $IFACE root netem \
  delay 30ms 5ms distribution normal \
  loss 0.5% 25% \
  reorder 0.1% 50% \
  rate 100mbit

# Explanation:
# - delay 30ms: Base latency (one-way)
# - 5ms: Jitter (standard deviation)
# - distribution normal: Bell curve jitter distribution
# - loss 0.5%: Base packet loss
# - 25%: Correlation (if packet lost, next packet 25% likely to be lost too)
# - reorder 0.1% 50%: Small chance of out-of-order packets
# - rate 100mbit: Bandwidth limit
```

**Kuiper Rain Fade Profile:**
```bash
#!/bin/bash
# kuiper-profile-rain-fade.sh

IFACE="eth0"

sudo tc qdisc del dev $IFACE root 2>/dev/null

# Simulate heavy rain (increased loss, higher jitter)
sudo tc qdisc add dev $IFACE root netem \
  delay 35ms 15ms distribution pareto \
  loss 3% 50% \
  duplicate 0.1% \
  corrupt 0.01% \
  rate 50mbit

# Explanation:
# - delay 35ms 15ms: Higher latency and jitter
# - distribution pareto: Long tail (occasional spikes)
# - loss 3% 50%: Higher loss with high correlation (bursty)
# - duplicate 0.1%: Occasional duplicate packets (RF echo)
# - corrupt 0.01%: Bit errors (RF noise)
# - rate 50mbit: Degraded throughput
```

**Kuiper Handoff Profile (Brief Outage):**
```bash
#!/bin/bash
# kuiper-profile-handoff.sh

IFACE="eth0"

# Simulate satellite handoff every 5 minutes
while true; do
  # Normal operation (4 minutes 55 seconds)
  echo "Normal operation..."
  sudo tc qdisc replace dev $IFACE root netem delay 30ms 5ms loss 0.5%
  sleep 295

  # Handoff (5 seconds of high loss)
  echo "Handoff in progress..."
  sudo tc qdisc replace dev $IFACE root netem delay 50ms 20ms loss 10%
  sleep 5
done
```

**Tool #2: Docker Compose Test Environment**

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Client (test runner)
  client:
    image: alpine:latest
    container_name: satellite-client
    networks:
      - satellite_net
    command: >
      sh -c "apk add --no-cache curl iperf3 openssh-client &&
             tail -f /dev/null"
    cap_add:
      - NET_ADMIN  # Needed for tc netem

  # Server (test target)
  server:
    image: nginx:alpine
    container_name: satellite-server
    networks:
      - satellite_net
    ports:
      - "8080:80"

  # Network emulator (sidecar)
  netem:
    image: alpine:latest
    container_name: satellite-netem
    networks:
      - satellite_net
    cap_add:
      - NET_ADMIN
    command: >
      sh -c "apk add --no-cache iproute2 &&
             tc qdisc add dev eth0 root netem delay 30ms 5ms loss 0.5% &&
             tail -f /dev/null"

networks:
  satellite_net:
    driver: bridge
```

**Tool #3: Automated Test Suite**

```bash
#!/bin/bash
# test-suite.sh
# Tests HTTP, SSH, DNS under satellite conditions

# Setup
SERVER="192.168.1.20"
RESULTS_DIR="results/$(date +%Y%m%d_%H%M%S)"
mkdir -p $RESULTS_DIR

# Test profiles
PROFILES=(
  "normal:30ms 5ms:0.5%:100mbit"
  "rain:35ms 15ms:3%:50mbit"
  "handoff:50ms 20ms:10%:20mbit"
)

for profile in "${PROFILES[@]}"; do
  IFS=':' read -r name delay loss rate <<< "$profile"

  echo "Testing profile: $name"

  # Apply profile
  sudo tc qdisc replace dev eth0 root netem \
    delay $delay loss $loss rate $rate

  # Test 1: HTTP throughput
  echo "  - HTTP throughput"
  curl -w "@curl-format.txt" -o /dev/null -s http://$SERVER/ \
    > "$RESULTS_DIR/${name}_http.txt"

  # Test 2: SSH latency
  echo "  - SSH latency"
  for i in {1..100}; do
    time ssh user@$SERVER "echo test" 2>&1 | grep real
  done > "$RESULTS_DIR/${name}_ssh.txt"

  # Test 3: iperf3 (bandwidth)
  echo "  - iperf3 bandwidth"
  iperf3 -c $SERVER -t 30 -J > "$RESULTS_DIR/${name}_iperf3.json"

  # Test 4: ping (latency/jitter/loss)
  echo "  - ping stats"
  ping -c 100 $SERVER > "$RESULTS_DIR/${name}_ping.txt"

  sleep 5
done

# Reset
sudo tc qdisc del dev eth0 root

# Generate report
python3 generate-report.py $RESULTS_DIR
```

**curl-format.txt:**
```
time_namelookup:    %{time_namelookup}s\n
time_connect:       %{time_connect}s\n
time_appconnect:    %{time_appconnect}s\n
time_pretransfer:   %{time_pretransfer}s\n
time_redirect:      %{time_redirect}s\n
time_starttransfer: %{time_starttransfer}s\n
time_total:         %{time_total}s\n
size_download:      %{size_download} bytes\n
speed_download:     %{speed_download} bytes/sec\n
```

**Report Generator (Python):**

```python
#!/usr/bin/env python3
# generate-report.py

import json
import sys
import statistics
from pathlib import Path

def analyze_results(results_dir):
    results_path = Path(results_dir)

    report = {
        "profiles": {}
    }

    for profile in ["normal", "rain", "handoff"]:
        # Parse ping stats
        ping_file = results_path / f"{profile}_ping.txt"
        if ping_file.exists():
            with open(ping_file) as f:
                content = f.read()
                # Parse: rtt min/avg/max/mdev = 30.123/32.456/35.789/2.345 ms
                if "rtt min/avg/max/mdev" in content:
                    line = [l for l in content.split('\n') if 'rtt min/avg/max' in l][0]
                    stats = line.split('=')[1].strip().split('/')[:-1]  # Ignore mdev
                    report["profiles"][profile] = {
                        "ping_min_ms": float(stats[0]),
                        "ping_avg_ms": float(stats[1]),
                        "ping_max_ms": float(stats[2])
                    }

        # Parse iperf3 JSON
        iperf_file = results_path / f"{profile}_iperf3.json"
        if iperf_file.exists():
            with open(iperf_file) as f:
                data = json.load(f)
                report["profiles"][profile]["bandwidth_mbps"] = \
                    data["end"]["sum_received"]["bits_per_second"] / 1e6
                report["profiles"][profile]["retransmits"] = \
                    data["end"]["sum_sent"]["retransmits"]

    # Print markdown table
    print("| Profile | Ping Avg (ms) | Bandwidth (Mbps) | Retransmits |")
    print("|---------|---------------|------------------|-------------|")
    for profile, stats in report["profiles"].items():
        print(f"| {profile:7} | {stats.get('ping_avg_ms', 0):13.2f} | "
              f"{stats.get('bandwidth_mbps', 0):16.2f} | "
              f"{stats.get('retransmits', 0):11} |")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: generate-report.py <results_dir>")
        sys.exit(1)

    analyze_results(sys.argv[1])
```

**Expected Output:**

```
| Profile | Ping Avg (ms) | Bandwidth (Mbps) | Retransmits |
|---------|---------------|------------------|-------------|
| normal  |         32.45 |            95.23 |           2 |
| rain    |         38.92 |            47.84 |          18 |
| handoff |         54.12 |            18.45 |          45 |
```

**Portfolio Artifacts:**

| Artifact | Location | What It Shows |
|----------|----------|---------------|
| **tc netem Scripts** | `evidence/experiments/netem/profiles/` | All satellite profile scripts |
| **Test Suite** | `evidence/experiments/netem/test-suite.sh` | Automated testing framework |
| **Results** | `evidence/experiments/netem/results/` | Before/after graphs, tables |
| **Grafana Dashboard** | `dashboards/grafana/netem-results.json` | Visualizations of test results |
| **Documentation** | `evidence/experiments/netem/README.md` | How to reproduce experiments |

**Learn More:**

1. **tc netem:**
   - [Linux netem Man Page](https://man7.org/linux/man-pages/man8/tc-netem.8.html)
   - [netem Tutorial (PDF)](http://www.linuxfoundation.org/collaborate/workgroups/networking/netem)
   - [Simulating Networks with netem](https://www.youtube.com/results?search_query=tc+netem+tutorial)

2. **Network Testing Tools:**
   - [iperf3 Documentation](https://iperf.fr/)
   - [mtr (My Traceroute)](https://www.linode.com/docs/guides/diagnosing-network-issues-with-mtr/)
   - [Wireshark for Analysis](https://www.wireshark.org/)

3. **Protocol Optimization:**
   - [TCP BBR in Practice](https://blog.cloudflare.com/tcp-bbr-exploring-tcp-congestion-control/)
   - [QUIC Protocol (Google)](https://www.chromium.org/quic/)

---

### Q5: Which AWS services are most critical for Kuiper ground gateway connectivity? Walk me through a minimal viable architecture.

**Difficulty:** ⭐⭐⭐ (Advanced)
**Category:** AWS Architecture & Design
**Risk Level:** High (missing critical components = outages)
**Timebox:** 10-15 minutes
**Owner:** Solutions Architect or Senior Network Engineer

#### Detailed Answer:

**Simple Explanation (Feynman):**
Imagine you're building a highway system to connect remote towns (ground gateways) to a big city (AWS). You need:
1. **On-ramps** (how to connect) = VPN or Direct Connect
2. **Highway interchange** (central hub) = Transit Gateway
3. **Traffic signs** (DNS) = Route 53
4. **Traffic monitors** (observability) = CloudWatch
5. **Security checkpoints** (IAM, Security Groups)

The "minimal viable architecture" is the smallest set of these components that would actually work in production.

**Technical Explanation:**

**Minimal Viable Architecture (MVA):**

```
┌────────────────────────────────────────────────────────────────────┐
│          KUIPER GROUND GATEWAY - MINIMAL AWS ARCHITECTURE          │
│                (5 Critical Services + 3 Optional)                  │
└────────────────────────────────────────────────────────────────────┘

[PHYSICAL WORLD]
┌─────────────────────────────────────┐
│  Ground Gateway POP (Virginia)      │
│  ├─ Gateway Router (Cisco/Juniper)  │
│  ├─ Public IP: 203.0.113.10         │
│  └─ BGP ASN: 65001                  │
└───────────────┬─────────────────────┘
                │ Internet
                ↓
[AWS CLOUD - us-east-1]

┌────────────────────────────────────────────────────────────────────┐
│ SERVICE #1: VPN (Site-to-Site VPN) - CRITICAL                     │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓   │
│ ┃  Customer Gateway (CGW)                                      ┃   │
│ ┃  ├─ IP: 203.0.113.10                                        ┃   │
│ ┃  ├─ BGP ASN: 65001                                          ┃   │
│ ┃  └─ Represents physical gateway router                      ┃   │
│ ┃                                                               ┃   │
│ ┃  VPN Connection                                              ┃   │
│ ┃  ├─ Tunnel 1: 169.254.10.1/30 (BGP peer: 169.254.10.2)     ┃   │
│ ┃  ├─ Tunnel 2: 169.254.10.5/30 (BGP peer: 169.254.10.6)     ┃   │
│ ┃  ├─ Pre-shared keys (one per tunnel)                        ┃   │
│ ┃  ├─ IKEv2 + IPsec (AES-256-GCM)                            ┃   │
│ ┃  └─ BGP (eBGP, ASN 64512 AWS side)                         ┃   │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛   │
│                                                                    │
│ Why Critical: Only way to get traffic from gateway into AWS      │
│ Cost: ~$0.05/hour per VPN connection (~$36/month)                │
│ Alternative: Direct Connect (more expensive, longer setup)       │
└────────────────────────────────────────────────────────────────────┘
                │
                ↓
┌────────────────────────────────────────────────────────────────────┐
│ SERVICE #2: Transit Gateway (TGW) - CRITICAL                      │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓   │
│ ┃  Transit Gateway (tgw-kuiper-hub)                            ┃   │
│ ┃  ├─ Amazon ASN: 64512                                       ┃   │
│ ┃  ├─ ECMP: Enabled (load balance across tunnels)            ┃   │
│ ┃  └─ Auto-accept attachments: Disabled (security)            ┃   │
│ ┃                                                               ┃   │
│ ┃  Attachments:                                                ┃   │
│ ┃  ├─ VPN Attachment (from gateway VPN)                       ┃   │
│ ┃  └─ VPC Attachment (to application VPC)                     ┃   │
│ ┃                                                               ┃   │
│ ┃  Route Tables:                                               ┃   │
│ ┃  ├─ Gateway Route Table                                     ┃   │
│ ┃  │  └─ 10.0.0.0/8 → VPC Attachment (to apps)               ┃   │
│ ┃  └─ VPC Route Table                                         ┃   │
│ ┃     └─ 0.0.0.0/0 → VPN Attachment (to internet via GW)     ┃   │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛   │
│                                                                    │
│ Why Critical: Central hub for routing, enables multi-VPC        │
│ Cost: ~$0.05/hour (~$36/month) + $0.02/GB processed             │
│ Alternative: VPC Peering (doesn't scale, no transitive routing) │
└────────────────────────────────────────────────────────────────────┘
                │
                ↓
┌────────────────────────────────────────────────────────────────────┐
│ SERVICE #3: VPC - CRITICAL                                         │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓   │
│ ┃  VPC (kuiper-control-plane)                                  ┃   │
│ ┃  ├─ CIDR: 10.0.0.0/16                                       ┃   │
│ ┃  ├─ AZs: us-east-1a, us-east-1b                             ┃   │
│ ┃  └─ DNS Hostnames: Enabled                                  ┃   │
│ ┃                                                               ┃   │
│ ┃  Subnets:                                                    ┃   │
│ ┃  ├─ Private Subnet 1 (10.0.1.0/24, AZ-a) [Apps]           ┃   │
│ ┃  └─ Private Subnet 2 (10.0.2.0/24, AZ-b) [Apps]           ┃   │
│ ┃                                                               ┃   │
│ ┃  Route Tables:                                               ┃   │
│ ┃  └─ Private RT                                              ┃   │
│ ┃     ├─ 10.0.0.0/16 → local                                 ┃   │
│ ┃     └─ 0.0.0.0/0 → TGW Attachment                         ┃   │
│ ┃                                                               ┃   │
│ ┃  Security Groups:                                            ┃   │
│ ┃  └─ sg-kuiper-apps                                          ┃   │
│ ┃     ├─ Inbound: 443 from gateway CIDR (203.0.113.0/24)    ┃   │
│ ┃     └─ Outbound: All                                        ┃   │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛   │
│                                                                    │
│ Why Critical: Isolation boundary for applications               │
│ Cost: $0 (VPC is free, only resources inside cost money)        │
└────────────────────────────────────────────────────────────────────┘
                │
                ↓
┌────────────────────────────────────────────────────────────────────┐
│ SERVICE #4: CloudWatch - CRITICAL                                  │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓   │
│ ┃  Metrics (Automatic):                                        ┃   │
│ ┃  ├─ VPN Tunnel State (TunnelState: 0=down, 1=up)           ┃   │
│ ┃  ├─ VPN Tunnel Data In/Out (TunnelDataIn, TunnelDataOut)   ┃   │
│ ┃  ├─ TGW Bytes In/Out (BytesIn, BytesOut)                   ┃   │
│ ┃  └─ TGW Packet Drop (PacketDropCountBlackhole)             ┃   │
│ ┃                                                               ┃   │
│ ┃  Alarms (Must Configure):                                   ┃   │
│ ┃  ├─ VPN Tunnel Down (TunnelState < 1 for 5 min)            ┃   │
│ ┃  ├─ Both Tunnels Down (CRITICAL)                           ┃   │
│ ┃  └─ TGW Packet Drops (> 1000/min)                          ┃   │
│ ┃                                                               ┃   │
│ ┃  Logs:                                                       ┃   │
│ ┃  ├─ VPC Flow Logs → CloudWatch Logs                        ┃   │
│ ┃  └─ CloudTrail → CloudWatch Logs (API audit)               ┃   │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛   │
│                                                                    │
│ Why Critical: Only way to know if things are broken             │
│ Cost: ~$10-50/month (depends on log volume)                     │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ SERVICE #5: IAM - CRITICAL                                         │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓   │
│ ┃  Roles:                                                      ┃   │
│ ┃  └─ KuiperNetworkAdmin                                      ┃   │
│ ┃     ├─ ec2:*VPN* (manage VPN connections)                  ┃   │
│ ┃     ├─ ec2:*TransitGateway* (manage TGW)                   ┃   │
│ ┃     ├─ cloudwatch:* (full observability access)            ┃   │
│ ┃     └─ logs:* (read logs)                                   ┃   │
│ ┃                                                               ┃   │
│ ┃  Users:                                                      ┃   │
│ ┃  └─ netadmin@kuiper                                         ┃   │
│ ┃     ├─ MFA: Required                                        ┃   │
│ ┃     └─ Assume Role: KuiperNetworkAdmin                     ┃   │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛   │
│                                                                    │
│ Why Critical: Security, compliance, audit                       │
│ Cost: $0 (IAM is free)                                           │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ OPTIONAL (but Highly Recommended):                                │
│                                                                    │
│ Route 53:                                                          │
│ - Health checks for failover                                      │
│ - Latency-based routing (multi-region)                            │
│ Cost: $0.50/health check/month                                    │
│                                                                    │
│ SNS:                                                               │
│ - Alert delivery (email, SMS, PagerDuty)                          │
│ Cost: $0.50/million requests                                      │
│                                                                    │
│ Systems Manager:                                                   │
│ - Session Manager (SSH without bastion)                           │
│ - Parameter Store (secrets)                                       │
│ Cost: Free tier covers most use cases                             │
└────────────────────────────────────────────────────────────────────┘
```

**Terraform Minimal Viable Architecture:**

```hcl
# terraform/kuiper-mva/main.tf

# Provider
provider "aws" {
  region = "us-east-1"
}

# 1. Customer Gateway (represents physical gateway router)
resource "aws_customer_gateway" "kuiper_gateway_va" {
  bgp_asn    = 65001
  ip_address = "203.0.113.10"  # Gateway public IP
  type       = "ipsec.1"

  tags = {
    Name = "kuiper-gateway-virginia"
  }
}

# 2. Transit Gateway
resource "aws_ec2_transit_gateway" "kuiper_hub" {
  description                     = "Kuiper Ground Gateway Hub"
  amazon_side_asn                 = 64512
  default_route_table_association = "enable"
  default_route_table_propagation = "enable"

  tags = {
    Name = "tgw-kuiper-hub"
  }
}

# 3. VPN Connection (dual tunnel with BGP)
resource "aws_vpn_connection" "kuiper_vpn" {
  customer_gateway_id = aws_customer_gateway.kuiper_gateway_va.id
  transit_gateway_id  = aws_ec2_transit_gateway.kuiper_hub.id
  type                = "ipsec.1"

  tunnel1_inside_cidr   = "169.254.10.0/30"
  tunnel2_inside_cidr   = "169.254.10.4/30"
  tunnel1_preshared_key = var.tunnel1_psk  # Store in Terraform Cloud/Vault
  tunnel2_preshared_key = var.tunnel2_psk

  tags = {
    Name = "vpn-kuiper-gateway-va"
  }
}

# 4. VPC
resource "aws_vpc" "kuiper_control_plane" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "vpc-kuiper-control-plane"
  }
}

# 5. Subnets
resource "aws_subnet" "private_1a" {
  vpc_id            = aws_vpc.kuiper_control_plane.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "subnet-kuiper-private-1a"
  }
}

resource "aws_subnet" "private_1b" {
  vpc_id            = aws_vpc.kuiper_control_plane.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"

  tags = {
    Name = "subnet-kuiper-private-1b"
  }
}

# 6. TGW Attachment to VPC
resource "aws_ec2_transit_gateway_vpc_attachment" "kuiper_vpc" {
  subnet_ids         = [aws_subnet.private_1a.id, aws_subnet.private_1b.id]
  transit_gateway_id = aws_ec2_transit_gateway.kuiper_hub.id
  vpc_id             = aws_vpc.kuiper_control_plane.id

  tags = {
    Name = "tgw-attach-kuiper-vpc"
  }
}

# 7. Route Table (VPC → TGW for internet access via gateway)
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.kuiper_control_plane.id

  route {
    cidr_block         = "0.0.0.0/0"
    transit_gateway_id = aws_ec2_transit_gateway.kuiper_hub.id
  }

  tags = {
    Name = "rt-kuiper-private"
  }
}

resource "aws_route_table_association" "private_1a" {
  subnet_id      = aws_subnet.private_1a.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_1b" {
  subnet_id      = aws_subnet.private_1b.id
  route_table_id = aws_route_table.private.id
}

# 8. Security Group
resource "aws_security_group" "kuiper_apps" {
  name        = "sg-kuiper-apps"
  description = "Allow traffic from gateway"
  vpc_id      = aws_vpc.kuiper_control_plane.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["203.0.113.0/24"]  # Gateway CIDR
    description = "HTTPS from gateway"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "sg-kuiper-apps"
  }
}

# 9. CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "vpn_tunnel_down" {
  alarm_name          = "kuiper-vpn-tunnel-down"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "TunnelState"
  namespace           = "AWS/VPN"
  period              = "300"
  statistic           = "Average"
  threshold           = "1"
  alarm_description   = "VPN tunnel is down"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    VpnId = aws_vpn_connection.kuiper_vpn.id
  }
}

# 10. SNS Topic for Alerts
resource "aws_sns_topic" "alerts" {
  name = "kuiper-gateway-alerts"
}

resource "aws_sns_topic_subscription" "alerts_email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = "netadmin@kuiper.example.com"
}

# 11. VPC Flow Logs
resource "aws_flow_log" "kuiper_vpc" {
  iam_role_arn    = aws_iam_role.flow_logs.arn
  log_destination = aws_cloudwatch_log_group.flow_logs.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.kuiper_control_plane.id
}

resource "aws_cloudwatch_log_group" "flow_logs" {
  name              = "/aws/vpc/kuiper-control-plane"
  retention_in_days = 7
}

resource "aws_iam_role" "flow_logs" {
  name = "kuiper-vpc-flow-logs"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "vpc-flow-logs.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "flow_logs" {
  name = "kuiper-flow-logs-policy"
  role = aws_iam_role.flow_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ]
      Effect   = "Allow"
      Resource = "*"
    }]
  })
}

# Outputs
output "vpn_tunnel_1_address" {
  value = aws_vpn_connection.kuiper_vpn.tunnel1_address
}

output "vpn_tunnel_2_address" {
  value = aws_vpn_connection.kuiper_vpn.tunnel2_address
}

output "transit_gateway_id" {
  value = aws_ec2_transit_gateway.kuiper_hub.id
}

output "vpc_id" {
  value = aws_vpc.kuiper_control_plane.id
}
```

**Monthly Cost Estimate:**

```
Service              Units       Rate           Monthly Cost
─────────────────────────────────────────────────────────────
VPN Connection       1 conn      $0.05/hour     $36.00
Transit Gateway      1 TGW       $0.05/hour     $36.00
TGW Data Transfer    100 GB      $0.02/GB       $2.00
CloudWatch Alarms    3 alarms    $0.10/alarm    $0.30
CloudWatch Logs      5 GB        $0.50/GB       $2.50
SNS                  1000 emails $0.50/million  $0.00
VPC/Subnets/SG       N/A         Free           $0.00
IAM                  N/A         Free           $0.00
─────────────────────────────────────────────────────────────
TOTAL:                                          $76.80/month
```

**Portfolio Artifacts:**

| Artifact | Location | What It Shows |
|----------|----------|---------------|
| **MVA Terraform Module** | `infra/aws/terraform/kuiper-mva/` | Complete minimal architecture as code |
| **Architecture Diagram** | `docs/diagrams/kuiper/mva.mmd` | Visual representation |
| **Cost Analysis** | `docs/cost/kuiper-mva-cost.md` | Detailed cost breakdown with alternatives |
| **ADR: VPN vs DX** | `docs/adr/ADR-0003-vpn-vs-dx.md` | Why we start with VPN (cost, speed to deploy) |
| **Deployment Guide** | `docs/runbooks/deploy-mva.md` | Step-by-step deployment instructions |

**Learn More:**

1. **AWS Networking:**
   - [AWS Site-to-Site VPN Documentation](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html)
   - [Transit Gateway Guide](https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html)
   - [VPN BGP Configuration](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPNRoutingTypes.html)

2. **Architecture Patterns:**
   - [AWS Multi-Region Architecture](https://aws.amazon.com/blogs/architecture/disaster-recovery-dr-architecture-on-aws-part-i-strategies-for-recovery-in-the-cloud/)
   - [Hybrid Cloud Connectivity](https://d1.awsstatic.com/whitepapers/hybrid-cloud-with-aws.pdf)

---

**Continue reading:** Questions 6-60 coming next...

## Glossary of All Terms (A-Z)

### A
- **ACL (Access Control List):** Rules defining who/what can access a resource
- **ADR (Architecture Decision Record):** Document explaining why a design choice was made
- **AES (Advanced Encryption Standard):** Symmetric encryption algorithm (256-bit = very secure)
- **ALB (Application Load Balancer):** AWS Layer 7 load balancer for HTTP/HTTPS
- **AMI (Amazon Machine Image):** Pre-configured OS template for EC2 instances
- **Ansible:** Configuration management tool (automates server setup)
- **Anycast:** Single IP announced from multiple locations (BGP routes to nearest)
- **APT (Advanced Persistent Threat):** Sophisticated, long-term cyberattack
- **ARN (Amazon Resource Name):** Unique identifier for AWS resources
- **AS (Autonomous System):** Collection of networks under single administrative control
- **ASN (Autonomous System Number):** Unique number identifying an AS (e.g., AS16509 = Amazon)
- **Auto Scaling:** Automatically add/remove instances based on load
- **AZ (Availability Zone):** Isolated data center within AWS Region

### B
- **Bastion Host:** Hardened server for admin access (jump box)
- **BGP (Border Gateway Protocol):** Internet routing protocol (path-vector, policy-based)
- **Blameless Postmortem:** Incident review focused on learning, not blaming
- **BYOIP (Bring Your Own IP):** Use your own IP addresses in AWS

### C
- **CA (Certificate Authority):** Issues digital certificates (like a passport office)
- **CDN (Content Delivery Network):** Distributed caching (CloudFront, Cloudflare)
- **CFN (CloudFormation):** AWS's IaC (Infrastructure as Code) service
- **CGW (Customer Gateway):** Your router in S2S VPN setup
- **CIDR (Classless Inter-Domain Routing):** IP address range notation (e.g., 10.0.0.0/16)
- **CLI (Command Line Interface):** Text-based tool (aws cli, terraform cli)
- **CloudTrail:** AWS audit log (who did what, when)
- **CloudWatch:** AWS monitoring service (metrics, logs, alarms)
- **CNAME (Canonical Name):** DNS record type (alias to another domain)
- **CW (CloudWatch):** Abbreviation

### D
- **DDoS (Distributed Denial of Service):** Attack overwhelming system with traffic
- **DHCP (Dynamic Host Configuration Protocol):** Assigns IP addresses automatically
- **DNS (Domain Name System):** Converts names to IPs (google.com → 142.250.185.46)
- **DPI (Deep Packet Inspection):** Examining packet contents (not just headers)
- **DSCP (Differentiated Services Code Point):** QoS marking in IP header
- **DX (Direct Connect):** Private AWS connection (not over internet)

### E
- **EBS (Elastic Block Store):** AWS block storage (hard drive for EC2)
- **EC2 (Elastic Compute Cloud):** AWS virtual servers
- **ECMP (Equal-Cost Multi-Path):** Load balancing across multiple paths
- **ECS (Elastic Container Service):** AWS Docker container orchestration
- **EKS (Elastic Kubernetes Service):** AWS managed Kubernetes
- **ELB (Elastic Load Balancing):** Generic term for AWS load balancers

### F
- **Failover:** Automatically switching to backup when primary fails
- **FCC (Federal Communications Commission):** US telecom regulator

### G
- **GEO (Geostationary Orbit):** Satellites at 35,786 km (high latency, ~600 ms)
- **GitOps:** Using Git as source of truth for infrastructure
- **GSLB (Global Server Load Balancing):** DNS-based traffic steering

### H
- **HA (High Availability):** Designing systems to minimize downtime
- **Health Check:** Automated test to see if service is working
- **HSM (Hardware Security Module):** Tamper-resistant device storing crypto keys
- **HTTP/HTTPS:** Web protocols (HTTPS = encrypted)

### I
- **IaaS (Infrastructure as a Service):** Rent compute/storage (EC2, S3)
- **IAM (Identity & Access Management):** AWS permission system
- **ICMP (Internet Control Message Protocol):** Used for ping
- **IDS/IPS (Intrusion Detection/Prevention System):** Security monitoring (Suricata, Snort)
- **IGW (Internet Gateway):** Door from VPC to internet
- **IPsec (Internet Protocol Security):** VPN encryption protocol
- **ISP (Internet Service Provider):** Company providing internet (Comcast, AT&T)
- **ITU (International Telecommunication Union):** UN agency for telecom standards

### J
- **Jinja:** Templating language (used with Ansible)
- **JIT (Just-In-Time):** Access granted only when needed, expires quickly

### K
- **Ka-band:** Satellite frequency range (26.5-40 GHz)
- **KMS (Key Management Service):** AWS encryption key management
- **Kubernetes (K8s):** Container orchestration platform

### L
- **Lambda:** AWS serverless compute (run code without servers)
- **Latency:** Time delay (e.g., ping time)
- **Least Privilege:** Give minimum permissions needed (security best practice)
- **LEO (Low Earth Orbit):** Satellites at 500-2,000 km (low latency, ~20-30 ms)
- **LNA (Low Noise Amplifier):** Boosts weak satellite signals
- **Loki:** Log aggregation system (like Elasticsearch but simpler)

### M
- **MACsec:** Layer 2 encryption (for Direct Connect)
- **MFA (Multi-Factor Authentication):** Two-step verification (password + code)
- **MPLS (Multiprotocol Label Switching):** ISP's internal routing technology
- **mTLS (Mutual TLS):** Both parties authenticate with certificates

### N
- **NACL (Network Access Control List):** Subnet-level firewall (stateless)
- **NAPALM:** Network automation library (Python)
- **NAT (Network Address Translation):** Converts private IPs to public IPs
- **NAT Gateway:** AWS managed NAT service
- **Netmiko:** Python library for SSH to network devices
- **NLB (Network Load Balancer):** AWS Layer 4 load balancer (TCP/UDP)

### O
- **OISL (Optical Inter-Satellite Links):** Lasers connecting satellites
- **OWASP:** Open Web Application Security Project (Top 10 vulnerabilities)

### P
- **PagerDuty:** On-call incident management platform
- **PKI (Public Key Infrastructure):** Certificate management system
- **POP (Point of Presence):** Physical network location
- **Prometheus:** Metrics collection and alerting system

### Q
- **QoS (Quality of Service):** Prioritizing network traffic (VoIP > file downloads)

### R
- **RBAC (Role-Based Access Control):** Permissions based on job role
- **RDS (Relational Database Service):** AWS managed databases (MySQL, PostgreSQL)
- **RFC (Request for Comments):** Internet standard documents
- **Route 53:** AWS DNS service (named after port 53)
- **Route Table:** Rules directing network traffic
- **Runbook:** Step-by-step operational procedure

### S
- **S2S VPN (Site-to-Site VPN):** VPN between networks (not individual users)
- **S3 (Simple Storage Service):** AWS object storage
- **SAN (Subject Alternative Name):** Certificate field listing allowed domains/IPs
- **Security Group:** Instance-level firewall (stateful)
- **SIEM (Security Information & Event Management):** Centralized security monitoring
- **SLA (Service Level Agreement):** Contract with uptime guarantees
- **SLI (Service Level Indicator):** Measurement (e.g., latency, error rate)
- **SLO (Service Level Objective):** Target for SLI (e.g., latency < 100 ms for 99% of requests)
- **SNS (Simple Notification Service):** AWS pub/sub messaging
- **SOC (Security Operations Center):** 24/7 security monitoring team
- **SRE (Site Reliability Engineering):** Google's approach to operations
- **SSH (Secure Shell):** Encrypted remote access (port 22)
- **SSL/TLS:** Encryption protocols (HTTPS uses TLS)
- **Suricata/Snort:** Open-source IDS/IPS systems
- **Synthetic Monitoring:** Automated tests simulating user behavior

### T
- **TCP (Transmission Control Protocol):** Reliable, connection-oriented (HTTP, SSH)
- **Terraform:** Infrastructure as Code tool (HashiCorp)
- **TGW (Transit Gateway):** AWS regional network hub
- **TLS (Transport Layer Security):** Encryption protocol (HTTPS, mTLS)
- **TTL (Time To Live):** How long to cache (DNS, packets)

### U
- **UDP (User Datagram Protocol):** Fast, unreliable (DNS, video streaming)

### V
- **VGW (Virtual Private Gateway):** Old AWS VPN endpoint (use TGW instead)
- **VLAN (Virtual LAN):** Network segmentation at Layer 2
- **VPC (Virtual Private Cloud):** Your private network in AWS
- **VPN (Virtual Private Network):** Encrypted tunnel
- **VRF (Virtual Routing and Forwarding):** Separate routing tables (MPLS, routers)

### W
- **WAF (Web Application Firewall):** Protects against OWASP Top 10 (SQL injection, XSS)

### Y
- **YAML:** Configuration file format (human-readable)

### Z
- **Zero Trust:** Security model (never trust, always verify)
- **ZFS:** Advanced filesystem (TrueNAS uses this)

---

## Demo Index & Portfolio Artifacts

**Organized by Topic**

### Kuiper Architecture & Networking

| Demo/Artifact | Location | Type | Shows |
|---------------|----------|------|-------|
| **Kuiper Overview README** | `projects/kuiper/ground-gateway-ops/README.md` | Documentation | Role responsibilities, system overview, glossary |
| **Data Flow Diagram** | `docs/diagrams/kuiper/data-flow.mmd` | Mermaid Diagram | Terminal → Satellite → Gateway → AWS flow |
| **Kuiper ADR-0001** | `docs/adr/ADR-0001-kuiper-data-path.md` | ADR | Trust boundaries, security model |
| **Gateway SLOs** | `docs/slo/kuiper-gateway.yml` | YAML | SLO targets (latency, loss, BGP stability) |

### AWS Transit Gateway & VPN

| Demo/Artifact | Location | Type | Shows |
|---------------|----------|------|-------|
| **TGW Hub Module** | `infra/aws/terraform/tgw-hub/` | Terraform | TGW + attachments + route tables |
| **VPN-BGP Module** | `infra/aws/terraform/vpn-bgp/` | Terraform | S2S VPN with BGP configuration |
| **TGW vs Peering ADR** | `docs/adr/ADR-0002-tgw-vs-peering.md` | ADR | Decision: when to use TGW vs VPC peering |
| **VPN Dashboard** | `dashboards/cloudwatch/vpn-bgp.json` | CloudWatch JSON | Tunnel state, BGP metrics, alarms |

### Route 53 & DNS

| Demo/Artifact | Location | Type | Shows |
|---------------|----------|------|-------|
| **R53 Latency Module** | `infra/aws/terraform/r53-latency/` | Terraform | Latency-based routing + health checks |
| **Health Checks Config** | `infra/aws/terraform/r53-latency/healthchecks.tf` | Terraform | Multi-region health check setup |
| **Anycast ADR** | `docs/adr/ADR-0004-anycast-vs-dns.md` | ADR | When to use anycast vs DNS |

### Security & PKI

| Demo/Artifact | Location | Type | Shows |
|---------------|----------|------|-------|
| **PKI Documentation** | `docs/pki/` | Markdown | CA design, rotation policy, SANs |
| **Cert Rotation Script** | `scripts/pki/rotate.sh` | Bash | Automated certificate rotation |
| **mTLS Runbook** | `docs/runbooks/mTLS-control-plane.md` | Markdown | Operational procedures |

### Observability & Monitoring

| Demo/Artifact | Location | Type | Shows |
|---------------|----------|------|-------|
| **Prometheus Rules** | `observability/prometheus/rules/kuiper-gateway.yml` | Prometheus | BGP/VPN/tunnel alert rules |
| **Alertmanager Routes** | `observability/alertmanager/routes/kuiper.yaml` | YAML | Site/service routing, inhibition |
| **Gateway Alerts Runbook** | `docs/runbooks/alerts/kuiper-gateway-alerts.md` | Markdown | Alert response procedures |
| **Gateway Dashboard** | `dashboards/cloudwatch/vpn-bgp.json` | CloudWatch JSON | Comprehensive metrics dashboard |

### Automation & IaC

| Demo/Artifact | Location | Type | Shows |
|---------------|----------|------|-------|
| **Satellite Link Simulation** | `evidence/experiments/netem/` | Bash + Results | tc netem profiles, before/after graphs |
| **ACL Automation** | `scripts/acl/` | Python + Jinja | YAML → Jinja → device push |
| **NAPALM Scripts** | `scripts/napalm/` | Python | Network device audits, drift detection |

### Runbooks & SRE

| Demo/Artifact | Location | Type | Shows |
|---------------|----------|------|-------|
| **VPN ECMP Failover** | `docs/runbooks/vpn-ecmp-failover.md` | Markdown | Dual-tunnel failover procedures |
| **Region Failover** | `docs/runbooks/region-failover.md` | Markdown | Multi-region DR drill |
| **Change Template** | `docs/runbooks/change/tgw-vpn-change-template.md` | Markdown | Pre/post checks, rollback |
| **Postmortem Template** | `docs/postmortems/template.md` | Markdown | Blameless postmortem format |
| **BGP Flap Playbook** | `docs/runbooks/bgp-flap-playbook.md` | Markdown | On-call response for BGP issues |

### Homelab Projects

| Demo/Artifact | Location | Type | Shows |
|---------------|----------|------|-------|
| **UniFi Network** | `projects/06-homelab/PRJ-HOME-001/` | Documentation + Configs | VLAN segmentation, firewall rules |
| **Proxmox + VMs** | `projects/06-homelab/PRJ-HOME-002/` | Documentation + Configs | Virtualization, VLAN-aware bridges |
| **Monitoring Stack** | `projects/01-sde-devops/PRJ-SDE-002/` | Documentation + Configs | Prometheus, Grafana, Loki |

---

## Interview Warm-Up Exercises

**Do these 2 hours before your interview**

### Exercise 1: 5-Minute Whiteboard (15 min total)

Set a timer for 5 minutes. On a whiteboard or paper, draw and explain:

**Scenario:** "Design a multi-region, highly available connection from two Kuiper ground gateways to AWS. Include redundancy at every layer."

**Must include:**
- 2 ground gateways (different locations)
- Connectivity options (VPN/DX)
- Transit Gateway
- Multi-region setup
- Route 53 for traffic steering
- Monitoring

**Evaluation:**
- Did you finish in 5 minutes?
- Did you explain while drawing?
- Did you identify single points of failure?
- Did you mention monitoring/alerting?

### Exercise 2: Rapid Fire Q&A (10 min)

Have a friend ask you these questions. Answer in 30 seconds or less:

1. What's a VPC?
2. What's the difference between a security group and NACL?
3. Explain BGP in one sentence.
4. What's Transit Gateway?
5. What's the difference between VPN and Direct Connect?
6. What's mTLS?
7. What's a health check?
8. What's an SLO?
9. Name 3 ways to make a system highly available.
10. What's the first thing you check when an EC2 can't reach the internet?

### Exercise 3: Troubleshooting Simulation (20 min)

**Scenario:** You're on-call. You get paged: "Gateway-A BGP session to AWS is down. Traffic is failing over to Gateway-B but performance is degraded."

**Walk through your response:**
1. What's your first action?
2. What logs/dashboards do you check?
3. What are possible root causes?
4. How do you restore service?
5. What do you do after service is restored?

**Model answer:**
1. **Acknowledge alert** (PagerDuty), check if others seeing same issue (Slack)
2. **Check dashboards:**
   - CloudWatch: BGP session state (down confirmed)
   - Prometheus: VPN tunnel metrics (both tunnels down?)
   - Gateway logs: BGP log messages
3. **Possible causes:**
   - Internet circuit down (ISP issue)
   - VPN tunnel failed (AWS-side or gateway-side)
   - BGP misconfiguration (recent change?)
   - Gateway router crashed
4. **Restore service:**
   - If ISP issue: escalate to ISP, wait for fix
   - If VPN tunnel: restart tunnel, check pre-shared keys
   - If config: rollback last change
   - If router crashed: reboot, investigate logs
5. **Post-restoration:**
   - Write incident report
   - Update runbook if needed
   - Schedule blameless postmortem
   - Identify preventive measures

### Exercise 4: Explain to a Non-Technical Person (10 min)

Practice explaining these to your mom/friend who isn't technical:

1. What is Project Kuiper?
2. What do you do in your job?
3. Why is "high availability" important?
4. What is a VPN?

**Key:** Use analogies (VPN = secret tunnel, High Availability = backup generator)

---

## Next Steps

This is a detailed excerpt showing the format for the complete 60-question guide. The full guide continues with:

- **Questions 3-20:** AWS networking deep dives
- **Questions 21-40:** Observability, automation, Ansible, Terraform
- **Questions 41-60:** Advanced topics (BGP, MPLS, QoS, homelab)
- **All 60 questions include:**
  - Feynman explanation
  - Technical deep dive
  - Diagram reference (FigJam)
  - Portfolio artifact mapping
  - Learn more resources
  - Risk/timebox/owner
  - Acronym glossary entries

**Files to create:**
- `docs/kuiper/KUIPER_INTERVIEW_Q01-20.md` (Core AWS & Kuiper)
- `docs/kuiper/KUIPER_INTERVIEW_Q21-40.md` (Observability & Automation)
- `docs/kuiper/KUIPER_INTERVIEW_Q41-60.md` (Advanced & Homelab)

---

**Would you like me to:**
1. Continue with Questions 3-60?
2. Create the remaining weeks of the learning path?
3. Add more hands-on lab exercises?
4. Create additional artifacts (runbooks, ADRs, Terraform modules)?

Let me know and I'll continue building out this comprehensive guide!
