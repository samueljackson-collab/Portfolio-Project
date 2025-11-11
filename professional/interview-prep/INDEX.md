# T-Mobile Interview Prep - Complete Package Index

**Company:** T-Mobile (via Denali Advanced Integration)
**Location:** Redmond, WA
**Status:** 🟡 IN PROGRESS - Core materials ready, full packages being developed
**Last Updated:** 2025-11-10

---

## 🎯 Overview

This directory contains comprehensive interview preparation packages for **four technical roles** at T-Mobile/Denali:

1. **[DevOps Engineer - Data Operations Systems](#1-devops-engineer---data-operations-systems)** (Hourly, $48-56/hr)
2. **[Backend Data & Snowflake Engineer](#2-backend-data--snowflake-engineer)** (Hourly, $48-56/hr)
3. **[Network Engineer II](#3-network-engineer-ii)** (Salary, $150K-190K/yr)
4. **[System/Network Administrator - Kuiper](#4-systemnetwork-administrator---kuiper)** (Amazon/Kuiper, COMPLETE ✅)

Each package includes:
- 📚 Expanded cheat sheets with Feynman explanations
- 📖 Comprehensive glossary (200+ terms per role)
- 🧪 Hands-on lab index (10-15 labs per role)
- 📅 2-week learning path with daily schedule
- 🎤 Interview warm-up questions (30+ per role)
- 🎥 Curated video resources (50+ per role)

---

## Quick Navigation

| Role | Directory | Status | Priority |
|------|-----------|--------|----------|
| **DevOps Engineer (Data Ops)** | [`devops-data-ops/`](devops-data-ops/) | 🟡 In Progress | HIGH |
| **Backend Data & Snowflake** | [`backend-snowflake/`](backend-snowflake/) | 🟡 In Progress | HIGH |
| **Network Engineer II** | [`network-engineer-ii/`](network-engineer-ii/) | 🟡 In Progress | MEDIUM |
| **Kuiper Sys/NetAdmin** | [`kuiper/`](kuiper/) | 🟢 Complete | Reference |

---

## 1. DevOps Engineer - Data Operations Systems

**Company:** T-Mobile
**Compensation:** $48-56/hr (Hourly with minimal benefits)
**Location:** Redmond, WA (On-site)
**Experience Required:** 3+ years DevOps Engineering

### Role Summary
Build and maintain cloud-native data operations systems using Python, Go, Kubernetes, Snowflake, and Azure. Focus on GitLab CI/CD pipelines, secure identity management (EntraID), and integration with data science teams.

### Key Technologies
- **Languages:** Python, Go
- **Cloud:** Azure (primary), AWS (S3, Lambda, SQS)
- **Container Orchestration:** Kubernetes, Helm
- **CI/CD:** GitLab CI/CD, GitOps workflows
- **Data:** Snowflake, Pandas, Snowpark, Polars, Spark
- **Observability:** Prometheus, Grafana, Splunk
- **Identity:** Azure EntraID (formerly Azure AD)

### Interview Prep Package Contents
📂 **[devops-data-ops/](devops-data-ops/)**
- **README.md** - Package overview and quick start
- **cheat-sheets/** - Q1-Q30 covering Kubernetes, Python, Go, Snowflake, Azure, CI/CD
- **glossary/** - DevOps, cloud, data engineering, observability terms
- **demos/** - 12 hands-on labs (Kubernetes deployments, GitLab CI/CD, Python microservices, Snowflake integration)
- **learning-paths/** - 2-week schedule focusing on Python/Go microservices, K8s, and data pipelines
- **warm-ups/** - 30+ interview questions (containerization, GitOps, data engineering, ML integration)
- **videos/** - 50+ curated resources for DevOps, Kubernetes, Snowflake, Azure

### Your Relevant Portfolio Projects
- ✅ `projects/07-aiml-automation/` - Python automation, data processing
- ✅ `projects/01-sde-devops/PRJ-SDE-001/` - CI/CD, automation, infrastructure
- ✅ `projects/02-cloud-architecture/PRJ-CLOUD-001/` - Cloud architecture patterns
- ✅ `projects/p09-cloud-native-poc/` - Cloud-native application development
- ✅ `projects/p18-k8s-cicd/` - Kubernetes and CI/CD integration
- ✅ `projects/06-homelab/PRJ-HOME-002/` - Kubernetes cluster (if you have one)

### Learning Priority
**Week 1:** Python microservices, Kubernetes basics, GitLab CI/CD, Docker
**Week 2:** Snowflake integration, Azure services, observability, ML model deployment

---

## 2. Backend Data & Snowflake Engineer

**Company:** T-Mobile
**Compensation:** $48-56/hr (Hourly with minimal benefits)
**Location:** Redmond, WA (On-site)
**Experience Required:** 3+ years Backend Data & Snowflake Engineering

### Role Summary
Design, build, and optimize ETL pipelines for data ingestion, transformation, and processing. Focus on Snowflake data warehouse management, Python/Apache Spark for big data workloads, and scalable data architecture.

### Key Technologies
- **Languages:** Python, SQL
- **Big Data:** Apache Spark, PySpark
- **Data Warehouse:** Snowflake (primary focus)
- **Databases:** Oracle, various data sources
- **ETL:** Custom Python pipelines, data transformation
- **Orchestration:** Apache Airflow (preferred), Azure Data Factory
- **Cloud:** AWS, Azure, or Google Cloud
- **Best Practices:** Data modeling, partitioning, clustering, indexing

### Interview Prep Package Contents
📂 **[backend-snowflake/](backend-snowflake/)**
- **README.md** - Package overview and quick start
- **cheat-sheets/** - Q1-Q30 covering Snowflake, ETL, Python/Spark, data modeling, SQL optimization
- **glossary/** - Data engineering, Snowflake, big data, data warehouse terms
- **demos/** - 12 hands-on labs (Snowflake setup, ETL pipelines, PySpark processing, data modeling, query optimization)
- **learning-paths/** - 2-week schedule focusing on Snowflake architecture, ETL design, and big data processing
- **warm-ups/** - 30+ interview questions (Snowflake internals, data modeling, ETL patterns, SQL optimization)
- **videos/** - 50+ curated resources for Snowflake, Apache Spark, data engineering, ETL

### Your Relevant Portfolio Projects
- ✅ `projects/p12-data-pipeline/` - Data pipeline architecture and implementation
- ✅ `projects/16-advanced-data-lake/` - Data lake architecture, processing
- ✅ `projects/5-real-time-data-streaming/` - Streaming data processing
- ✅ `projects/7-serverless-data-processing/` - Serverless data pipelines
- ✅ `projects/08-web-data/PRJ-WEB-001/` - Data collection and processing
- ✅ `projects/6-mlops-platform/` - Data pipelines for ML workflows

### Learning Priority
**Week 1:** Snowflake fundamentals, SQL optimization, data modeling, Python for data
**Week 2:** Apache Spark/PySpark, ETL design patterns, data warehouse best practices, performance tuning

---

## 3. Network Engineer II

**Company:** Denali Advanced Integration (supporting T-Mobile/Microsoft)
**Compensation:** $150K-190K/year (Salary with full benefits)
**Location:** Redmond, WA (On-site required)
**Experience Required:** 5-10 years network engineering

### Role Summary
Provide enterprise network architecture, support, and operations for 5K+ network devices. Focus on routing/switching, security, wireless, VoIP, documentation, and leading complex network projects. Act as technical lead and mentor to junior engineers.

### Key Technologies
- **Vendors:** Cisco (primary), Juniper, Foundry
- **Certifications:** CCNA, CCNP, CCIE (plus)
- **Protocols:** MSTP, 802.1q, 802.1AX, TRILL, OSPF, ISIS, BGP, MPLS, LDP
- **L4-7:** TCP, SSL, HTTP, DNS, NTP, load balancing (local & global)
- **Security:** Firewalls, IDS, VPN, Radius, TACACS+, LDAP
- **Wireless:** Enterprise wireless (802.11 standards)
- **Tools:** Wireshark/Netmon, packet captures, network scanning
- **Monitoring:** Enterprise network monitoring platforms
- **Frameworks:** ITIL

### Interview Prep Package Contents
📂 **[network-engineer-ii/](network-engineer-ii/)**
- **README.md** - Package overview and quick start
- **cheat-sheets/** - Q1-Q30 covering routing protocols, switching, security, wireless, troubleshooting
- **glossary/** - Networking protocols, Cisco/Juniper, security, wireless, ITIL terms
- **demos/** - 12 hands-on labs (GNS3/EVE-NG routing, switching VLANs, firewall rules, BGP/OSPF/ISIS, wireless)
- **learning-paths/** - 2-week schedule focusing on routing protocols, enterprise networking, and Cisco/Juniper platforms
- **warm-ups/** - 30+ interview questions (protocol deep dives, troubleshooting scenarios, design decisions)
- **videos/** - 50+ curated resources for CCNP-level topics, enterprise networking, Cisco/Juniper

### Your Relevant Portfolio Projects
- ✅ `projects/05-networking-datacenter/PRJ-NET-DC-001/` - Datacenter networking, VLANs, routing
- ✅ `projects/06-homelab/PRJ-HOME-002/` - Enterprise-grade homelab with VLANs, routing, security
- ✅ `projects/p03-hybrid-network/` - Hybrid networking, VPN, BGP (from Kuiper prep)
- ✅ `projects/p07-roaming-simulation/` - Network simulation and handoff scenarios
- ✅ `projects/03-cybersecurity/PRJ-CYB-OPS-002/` - Network security operations

### Learning Priority
**Week 1:** Routing protocols (OSPF, ISIS, BGP, MPLS), advanced switching, Cisco IOS
**Week 2:** Network security (firewalls, IDS, VPN), wireless enterprise, troubleshooting, leadership

---

## 4. System/Network Administrator - Kuiper

**Company:** Amazon (Project Kuiper)
**Status:** ✅ **COMPLETE PACKAGE AVAILABLE**
**Location:** TBD (likely Seattle area or ground gateway locations)

### Interview Prep Package
📂 **[kuiper/](kuiper/)** ← **REFERENCE THIS AS TEMPLATE**

This is the **gold standard** for interview prep structure. All other packages follow this model with role-specific content.

**What's included:**
- ✅ 2 expanded cheat sheets (Q1-Q20) with Feynman explanations, acronyms, examples, pitfalls
- ✅ Comprehensive glossary (200+ AWS, networking, satellite, SRE terms)
- ✅ 15 hands-on labs (TC netem, VPC, TGW, VPN+BGP, Route 53, mTLS, dual-gateway HA, chaos)
- ✅ 2-week learning path with daily schedules, risk ratings, timeboxes
- ✅ 30+ interview warm-up questions (Easy/Medium/Hard/Behavioral)
- ✅ 50+ curated video resources
- ✅ Professional README with quick start and motivation

---

## 📊 Comparison Matrix

| Feature | DevOps Engineer | Backend Data Engineer | Network Engineer II | Kuiper Sys/NetAdmin |
|---------|----------------|---------------------|-------------------|-------------------|
| **Focus** | Cloud-native DevOps + Data | ETL + Snowflake | Enterprise Networking | Ground Gateway + AWS |
| **Primary Tech** | K8s, Python, Go, Azure | Snowflake, Spark, SQL | Cisco, BGP, OSPF, Security | AWS, BGP, VPN, TGW |
| **Compensation** | $48-56/hr (~$100-117K/yr) | $48-56/hr (~$100-117K/yr) | $150-190K/yr | TBD (likely $120-180K) |
| **Experience** | 3+ years | 3+ years | 5-10 years | 3-5 years (estimated) |
| **Certifications** | None required | Snowflake (preferred) | CCNA/CCNP/CCIE | AWS certs (preferred) |
| **Interview Difficulty** | 🟡 Medium | 🟡 Medium | 🔴 High | 🔴 High |
| **Learning Curve** | Moderate (if familiar with DevOps) | Moderate (if familiar with data) | Steep (broad protocol knowledge) | Steep (satellite + AWS + BGP) |

---

## 🚀 Which Role Should You Prioritize?

### Based on Compensation
1. **Network Engineer II** - $150-190K (highest salary, full benefits)
2. **DevOps Engineer** - $100-117K equivalent (hourly, limited benefits)
3. **Backend Data Engineer** - $100-117K equivalent (hourly, limited benefits)

### Based on Your Strengths (from portfolio)
1. **Network Engineer II** - You have strong networking background (homelab, Kuiper BGP/VPN prep)
2. **DevOps Engineer** - You have Python, automation, cloud architecture, Kubernetes projects
3. **Backend Data Engineer** - You have data pipeline and processing projects

### Based on Interview Prep Time
1. **DevOps Engineer** - 2 weeks (builds on existing cloud/K8s knowledge)
2. **Backend Data Engineer** - 2 weeks (focused on Snowflake, ETL patterns)
3. **Network Engineer II** - 3-4 weeks (broadest protocol knowledge required, most certifications)

### Strategic Recommendation
**Option A: Go for Highest Compensation**
1. Focus on **Network Engineer II** (3-4 weeks prep, highest salary)
2. Use Kuiper prep as foundation (BGP, routing, troubleshooting mindset)
3. Add Cisco/Juniper specifics, OSPF/ISIS, enterprise wireless

**Option B: Quick Win Strategy**
1. Apply to all three roles simultaneously
2. Prepare **DevOps Engineer** first (2 weeks, builds on existing strengths)
3. If you get DevOps interview, use that experience to refine prep for others
4. Leverage common skills (Python, cloud, troubleshooting, communication)

**Option C: Diversified Approach**
1. Prepare core materials for all three in parallel (Week 1: common foundations)
2. Week 2: Role-specific deep dives based on which interviews you secure
3. Advantage: Flexibility to pivot based on interview scheduling

---

## 📅 Suggested Timeline

### Scenario 1: Preparing for All Three Roles

**Week 1-2: Common Foundations**
- Python proficiency (applies to DevOps + Data roles)
- Cloud fundamentals (Azure + AWS review)
- SQL and data concepts (applies to Data + DevOps roles)
- Networking refresher (applies to NetEng + DevOps roles)
- STAR method behavioral prep (applies to all)

**Week 3: Role-Specific Deep Dive (Based on Interview Schedule)**
- DevOps: Kubernetes, GitLab CI/CD, Snowflake integration, microservices
- Data: Snowflake deep dive, Apache Spark, ETL patterns, data modeling
- NetEng: Cisco IOS deep dive, OSPF/ISIS/BGP, enterprise wireless, security

**Week 4: Interview Practice & Polish**
- Mock interviews for each role
- Portfolio cleanup and mapping to each role's requirements
- Technical question practice (role-specific warm-ups)
- Prepare questions to ask interviewers

---

## 🎯 Action Plan (Starting Today)

### Step 1: Choose Your Strategy (5 minutes)
- [ ] Read comparison matrix above
- [ ] Decide: Option A (Network Eng II), Option B (DevOps first), or Option C (All three parallel)
- [ ] Set interview target dates

### Step 2: Review Existing Packages (30 minutes)
- [ ] Read `kuiper/README.md` to understand structure
- [ ] Skim one cheat sheet to see format
- [ ] Review one lab to understand expectations

### Step 3: Start Your Chosen Path (Today!)
**If DevOps Engineer:**
- [ ] Read `devops-data-ops/README.md`
- [ ] Start Lab 01: Kubernetes basics (deploy sample app)
- [ ] Watch Python microservices video

**If Backend Data Engineer:**
- [ ] Read `backend-snowflake/README.md`
- [ ] Start Lab 01: Snowflake trial account setup
- [ ] Watch Snowflake fundamentals video

**If Network Engineer II:**
- [ ] Read `network-engineer-ii/README.md`
- [ ] Start Lab 01: GNS3/EVE-NG setup (or use Packet Tracer)
- [ ] Watch OSPF deep dive video

---

## 📂 Directory Structure

```
professional/interview-prep/
├── INDEX.md (this file)
├── devops-data-ops/
│   ├── README.md
│   ├── cheat-sheets/
│   ├── glossary/
│   ├── demos/
│   ├── learning-paths/
│   ├── warm-ups/
│   └── videos/
├── backend-snowflake/
│   ├── README.md
│   ├── cheat-sheets/
│   ├── glossary/
│   ├── demos/
│   ├── learning-paths/
│   ├── warm-ups/
│   └── videos/
├── network-engineer-ii/
│   ├── README.md
│   ├── cheat-sheets/
│   ├── glossary/
│   ├── demos/
│   ├── learning-paths/
│   ├── warm-ups/
│   └── videos/
└── kuiper/ (COMPLETE ✅)
    ├── README.md
    ├── cheat-sheets/
    ├── glossary/
    ├── demos/
    ├── learning-paths/
    ├── warm-ups/
    └── videos/
```

---

## 🆘 Need Help?

### If You're Overwhelmed
1. **Don't try to do all three at once** (unless Option C and you're superhuman)
2. **Pick one role** based on compensation, your strengths, or interview timeline
3. **Use the Kuiper package as a template** - it shows you exactly what "done" looks like
4. **Start with labs** - hands-on work beats passive reading

### If You're Short on Time
1. **Focus on cheat sheets** - high-density knowledge in tables
2. **Do 3-5 core labs per role** (not all 15)
3. **Practice interview warm-ups** - 30 min/day is enough
4. **Map to existing portfolio** - you've already done relevant work!

### If You Get Stuck
1. Review Kuiper materials for structure/format examples
2. Reach out to peers/mentors who work in these roles
3. Join online communities (Reddit r/devops, r/dataengineering, r/networking)
4. Remember: Progress > Perfection

---

## 💪 You've Got This!

You've already proven you can learn complex technical topics systematically (you completed the Kuiper prep!). These three roles are well within your capability:

- **DevOps Engineer:** You have cloud, Python, and automation experience
- **Backend Data Engineer:** You have data pipeline and processing projects
- **Network Engineer II:** You have networking fundamentals + homelab + Kuiper networking prep

**The work is already done in your portfolio—now it's just about organizing your knowledge and presenting it confidently in interviews.**

---

**Next Steps:**
1. Choose your priority role (5 min)
2. Read that role's README (10 min)
3. Start Lab 01 for that role (today!)

**Good luck! 🚀**

---

**Last Updated:** 2025-11-10
**Status:** Core structure ready, full materials in development
**Maintained By:** [Your Name]
