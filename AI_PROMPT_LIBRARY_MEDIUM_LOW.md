# AI Prompt Library - Medium & Low Priority

## Complete Guide to Portfolio Enhancement (Part 2 of 3)

**Part 1:** See `AI_PROMPT_LIBRARY.md` for Critical & High priority prompts
**Part 2:** This document (Medium & Low priorities)
**Part 3:** See `AI_PROMPT_EXECUTION_FRAMEWORK.md` for execution strategies

### Master Factory Alignment (Required for Every Prompt Here)
- **Ship runnable assets:** Every output must include a runnable asset pack (code, configs, sample data, docs) that can be executed or previewed without additional authoring.
- **Follow the startup recipe:** Use the Master Factory startup recipe to bootstrap, package, and validate deliverables so they launch cleanly. See the quick link to the recipe in `AI_PROMPT_EXECUTION_FRAMEWORK.md` and mirror its steps when drafting prompts.
- **Close with the checklist:** Before marking a prompt done, run through `PROJECT_COMPLETION_CHECKLIST.md` to verify environments, documentation, and QA gates are covered.
- **Embed links in prompts:** Each prompt below explicitly references the startup recipe and checklist to keep Medium/Low workstreams aligned with the Master Factory rules.

---

## 🟡 Medium Priority (Complete Within 3 Months)

### MED-001: Complete Observability Stack Project

**Purpose:** Standalone monitoring project separate from homelab  
**Priority:** Medium (demonstrates specialized expertise)  
**Time Savings:** 12-15 hours  
**AI Tool:** Claude (handles complex multi-component systems)  
**Input Required:** Monitoring requirements, target infrastructure

**Prompt:**
```
Create a complete enterprise observability stack project demonstrating production monitoring best practices.

Master Factory delivery guardrails:
- Provide a runnable asset pack (code, configs, sample data, docs) that can be executed per the Master Factory startup recipe in `AI_PROMPT_EXECUTION_FRAMEWORK.md`.
- Include a quickstart and verification notes aligned to `PROJECT_COMPLETION_CHECKLIST.md` to confirm the stack launches cleanly.

PROJECT OVERVIEW:
Name: Enterprise Observability Stack
Purpose: Full-stack monitoring solution with metrics, logs, traces, and alerting
Target Infrastructure: Kubernetes cluster with microservices
Tech Stack: Prometheus, Grafana, Loki, Tempo, Alertmanager, OpenTelemetry

DELIVERABLES REQUIRED:

1. ARCHITECTURE DOCUMENTATION (Markdown)
   - Problem statement: Why observability matters (MTTD, MTTR metrics)
   - Three pillars: Metrics, Logs, Traces
   - Component interaction diagram (Mermaid)
   - Data flow from application → storage → visualization
   - High availability design (redundancy, retention policies)
   - Cost analysis (storage requirements, scaling considerations)

2. INFRASTRUCTURE CODE (Kubernetes manifests or Helm)
   k8s/monitoring/
   ├── namespace.yaml
   ├── prometheus/
   │   ├── deployment.yaml
   │   ├── service.yaml
   │   ├── configmap-prometheus.yaml      # Scrape configs
   │   ├── configmap-rules.yaml           # Alert rules
   │   ├── servicemonitor-crd.yaml
   │   └── persistentvolumeclaim.yaml     # Metrics storage
   ├── grafana/
   │   ├── deployment.yaml
   │   ├── service.yaml
   │   ├── ingress.yaml
   │   ├── configmap-datasources.yaml     # Prometheus, Loki, Tempo
   │   ├── configmap-dashboards.yaml      # Dashboard definitions
   │   └── persistentvolumeclaim.yaml     # Dashboard storage
   ├── loki/
   │   ├── statefulset.yaml               # Log storage
   │   ├── service.yaml
   │   ├── configmap.yaml                 # Loki configuration
   │   └── persistentvolumeclaim.yaml
   ├── promtail/
   │   ├── daemonset.yaml                 # Log collection agents
   │   └── configmap.yaml                 # Log parsing rules
   ├── tempo/
   │   ├── deployment.yaml                # Trace storage
   │   ├── service.yaml
   │   └── configmap.yaml
   ├── alertmanager/
   │   ├── deployment.yaml
   │   ├── service.yaml
   │   └── configmap-routing.yaml         # Alert routing rules
   └── opentelemetry/
       ├── deployment.yaml                # OTel collector
       ├── service.yaml
       └── configmap.yaml                 # Collection pipeline

3. PROMETHEUS CONFIGURATION
   - Global scrape interval: 15s
   - Scrape targets: API server, kubelet, node exporter, cAdvisor, ServiceMonitors
   - Recording rules for aggregations (reduce query time)
   - Alert rules with severity levels (warning, critical)

4. ALERT RULES (15-20 production-grade alerts)
   - Infrastructure: CPU/Mem/Disk, NodeNotReady, PodCrashLooping
   - Application: HighErrorRate, SlowResponseTime, Traffic spikes, ServiceDown
   - Database: Connection pool, Slow queries, Replication lag
   - Monitoring stack: PrometheusTargetDown, AlertmanagerFailedNotifications, HighSeriesChurn

5. GRAFANA DASHBOARDS (5-7 JSON exports)
   - Infrastructure overview, Application performance, Database metrics, Kubernetes resources, Alerts & SLOs

6. LOKI LOG AGGREGATION
   - LogQL examples
   - Promtail pipeline stages (JSON parsing, labels, drop rules)
   - Retention policy: 30 days

7. OPENTELEMETRY TRACING
   - Sample application instrumented with OTel SDK
   - Trace pipeline (App → OTel Collector → Tempo)
   - Example trace queries (slow requests, errors, dependencies)

8. ALERTMANAGER ROUTING
   - Route by severity (PagerDuty, Slack #incidents, #alerts, #monitoring)
   - Grouping rules and inhibitions (e.g., suppress pod alerts if node down)
   - Maintenance window silences

9. DEPLOYMENT GUIDE (Markdown)
   - Prerequisites (K8s 1.25+, kubectl, Helm, storage class)
   - Step-by-step deployment commands
   - Troubleshooting Prometheus, Grafana, Loki, Alertmanager

10. BEST PRACTICES DOCUMENT
    - Metric naming conventions, label cardinality, recording rules
    - Dashboard design principles (RED, USE)
    - Alert design (actionable, symptoms vs. causes)
    - Log sampling strategies, retention tuning

11. SAMPLE APPLICATION
    - Instrumented microservice (Node.js or Python)
    - Prometheus metrics endpoint, OTel traces, structured logs
    - Endpoints: /health, /api/users, /api/users POST, /slow, /error

12. COMPREHENSIVE README
    - Architecture, deployment, dashboards, queries, alerts
    - Cost optimization, scaling, security hardening, lessons learned

QUALITY REQUIREMENTS:
- `kubectl apply --dry-run=client` clean
- Alert rules tested
- Dashboards validated
- Security: RBAC, external secrets
- Resource limits on all deployments

OUTPUT STRUCTURE:
observability-stack/
├── README.md
├── docs/
│   ├── architecture.md
│   ├── deployment-guide.md
│   ├── troubleshooting.md
│   ├── best-practices.md
│   └── diagrams/
│       ├── architecture.png
│       └── data-flow.png
├── k8s/monitoring/
├── sample-app/
├── dashboards/
├── alerts/
└── examples/
```

**Post-Processing:**
1. Deploy to kind/minikube and validate
2. Verify Grafana datasources and dashboards
3. Trigger alert tests and capture screenshots
4. Record short demo video
5. Publish blog post summarizing architecture

---

### MED-002: Network Segmentation Standalone Project

**Purpose:** Dedicated network engineering project  
**Priority:** Medium  
**Time Savings:** 8-10 hours  
**AI Tool:** Claude  
**Input Required:** Existing network requirements and hardware inventory

**Prompt:**
```
Create a comprehensive network segmentation project demonstrating enterprise security practices.

Master Factory delivery guardrails:
- Ship runnable configs, scripts, sample data, and docs that can be applied directly using the startup recipe steps in `AI_PROMPT_EXECUTION_FRAMEWORK.md`.
- Add quickstart validation steps tied to `PROJECT_COMPLETION_CHECKLIST.md` so the lab build passes smoke checks.

PROJECT: Secure Network Architecture with VLAN Segmentation

SCENARIO:
Small business with 50 users needs secure network design.

DELIVERABLES:
1. NETWORK DESIGN DOCUMENT (2000+ words)
   - Executive summary, topology diagrams, VLAN tables
   - Security zones, inter-VLAN routing rules
2. NETWORK DIAGRAMS
   - Mermaid + PNG exports for physical, logical, and data flow
3. FIREWALL RULESETS
   - iptables or pfSense configurations with logging and rate limits
4. SWITCH CONFIGURATION
   - Cisco/HP syntax (VLAN creation, trunk/access ports, STP, DHCP snooping)
5. DHCP SERVER CONFIGURATION
   - Per-VLAN scopes, DNS, lease times, option 82
6. DNS CONFIGURATION
   - Split-horizon, DNSSEC validation, filtering for guest network
7. SECURITY MEASURES DOCUMENT
   - Defense in depth, wireless security, port security, IDS/IPS
8. IMPLEMENTATION PLAN
   - Phased rollout, rollback strategy, training
9. TESTING & VALIDATION GUIDE
   - Connectivity, security, performance, failure scenarios
10. MONITORING & MAINTENANCE
    - Grafana dashboards, SNMP, syslog, alerts, review cadence
11. COMPLIANCE MAPPING
    - PCI-DSS, HIPAA, SOC 2 references
12. COMPREHENSIVE README
    - Business justification, quick start, troubleshooting, roadmap

OUTPUT STRUCTURE:
network-segmentation/
├── README.md
├── docs/
│   ├── network-design.md
│   ├── implementation-plan.md
│   ├── security-measures.md
│   ├── testing-validation.md
│   ├── compliance-mapping.md
│   └── diagrams/
├── configs/
├── scripts/
└── monitoring/
```

**Post-Processing:**
1. Validate configs on lab equipment or simulators
2. Generate final diagrams via Mermaid CLI
3. Capture Grafana dashboard screenshots
4. Cross-check compliance mapping with references
5. Package scripts with usage instructions

---

### MED-003: PostgreSQL High Availability Project

**Purpose:** Demonstrate database administration and HA design  
**Priority:** Medium  
**Time Savings:** 10-12 hours  
**AI Tool:** Claude  
**Input Required:** Target environment (Docker, VMs), capacity requirements

**Prompt:**
```
Create a complete PostgreSQL high availability cluster project.

Master Factory delivery guardrails:
- Deliver runnable assets (compose files, configs, seed data, docs) that follow the startup recipe steps in `AI_PROMPT_EXECUTION_FRAMEWORK.md`.
- Embed smoke-test commands and checklist references from `PROJECT_COMPLETION_CHECKLIST.md` to prove the cluster spins up and fails over cleanly.

ARCHITECTURE:
- Primary + 2 synchronous replicas + 1 asynchronous replica
- Patroni + etcd for failover, HAProxy for routing, PgBouncer for pooling
- Barman for backups, exporters for monitoring

DELIVERABLES:
1. ARCHITECTURE DOCUMENTATION (3000+ words)
2. DOCKER COMPOSE IMPLEMENTATION with etcd, PostgreSQL nodes, Patroni, HAProxy, PgBouncer, Barman
3. POSTGRESQL CONFIGURATION FILES (postgresql.conf, pg_hba.conf, recovery.conf template)
4. PATRONI CONFIGURATION
5. HAPROXY CONFIGURATION (write/read pools, health checks)
6. PGBOUNCER CONFIGURATION (pooling modes, auth)
7. BACKUP STRATEGY WITH BARMAN (retention, compression, off-site replication)
8. MONITORING SETUP (Prometheus exporter, Grafana dashboards, alerts)
9. FAILOVER TESTING PROCEDURES (planned/unplanned, partition, restart)
10. PERFORMANCE TUNING GUIDE
11. DISASTER RECOVERY PLAYBOOK
12. OPERATIONS RUNBOOK
13. COMPREHENSIVE README (installation, operations, troubleshooting)

OUTPUT STRUCTURE:
postgresql-ha-cluster/
├── README.md
├── docs/
├── docker/
├── configs/
├── scripts/
├── monitoring/
└── tests/
```

**Post-Processing:**
1. Run `docker compose up` and validate failover scenarios
2. Test replication lag alerts and Grafana dashboards
3. Verify Barman backups and restore drills
4. Capture replication topology diagrams
5. Record benchmark results for README

---

### MED-004: QA Automation Framework (If Targeting QA Roles)

**Purpose:** End-to-end QA automation suite  
**Priority:** Medium (only if pursuing QA roles)  
**Time Savings:** 18-20 hours  
**AI Tool:** Claude or ChatGPT  
**Input Required:** Target application endpoints, supported browsers

**Prompt:**
```
Create a comprehensive end-to-end QA automation framework.

Master Factory delivery guardrails:
- Provide runnable automation assets (framework code, configs, sample data, docs) wired to the startup recipe in `AI_PROMPT_EXECUTION_FRAMEWORK.md`.
- Include quickstart/run instructions and QA checkpoints that map to `PROJECT_COMPLETION_CHECKLIST.md`.

REQUIREMENTS:
- Test pyramid (unit, integration, e2e, performance, security)
- Python (Pytest) or JavaScript stack (Playwright) with POM design
- API clients, fixtures, utilities, reporting, CI/CD workflows
- Detailed documentation, best practices, README
```

**Post-Processing:**
1. Align with actual application endpoints
2. Configure CI secrets for browser drivers or cloud testing
3. Run each layer of tests and archive reports
4. Capture Allure report screenshots
5. Document known flaky tests and mitigation

---

### MED-005: Technical Blog Post Generator

**Purpose:** Publish technical thought leadership content  
**Priority:** Medium  
**Time Savings:** 4-6 hours per post  
**AI Tool:** Claude or ChatGPT  
**Input Required:** Topic selection, personal anecdotes, screenshots

**Prompt:**
```
Create a comprehensive technical blog post.

Master Factory delivery guardrails:
- Bundle runnable/supporting assets (code snippets in repos, config examples, draft images, docs) with links to the startup recipe flow in `AI_PROMPT_EXECUTION_FRAMEWORK.md`.
- Add a publication-ready checklist reference to `PROJECT_COMPLETION_CHECKLIST.md` so SEO, QA, and linking steps are verifiable.

TOPIC: Choose from "Building a Production Homelab", "Terraform Best Practices", "PostgreSQL Performance Tuning", "Kubernetes Monitoring with Prometheus"

REQUIREMENTS:
- 2000-3000 words with SEO headline, meta description, ToC
- Practical examples, code snippets, pitfalls, visuals, CTA
- Tone: technical but approachable, include personal lessons
```

**Post-Processing:**
1. Add real screenshots/diagrams
2. Link to live repositories and documentation
3. Optimize metadata for the publishing platform
4. Proofread for voice consistency
5. Cross-link between related posts for SEO

---

### MED-006: GitHub Profile Optimization

**Purpose:** Improve recruiter visibility on GitHub  
**Priority:** Medium  
**Time Savings:** 2-3 hours  
**AI Tool:** Claude or ChatGPT  
**Input Required:** List of top repositories, bio preferences, stats

**Prompt:**
```
Optimize my GitHub profile for maximum recruiter visibility.

Master Factory delivery guardrails:
- Provide runnable asset updates (profile README, workflow configs, data-driven badges) with a quickstart aligned to the startup recipe in `AI_PROMPT_EXECUTION_FRAMEWORK.md`.
- Include a closing validation checklist tied to `PROJECT_COMPLETION_CHECKLIST.md` to confirm links, badges, and workflows work as shipped.

DELIVERABLES:
1. PROFILE README (hero, skills, featured projects, stats, contact)
2. REPOSITORY OPTIMIZATION CHECKLIST (naming, README, tags, license, templates)
3. CONTRIBUTION STRATEGY (activity cadence, OSS engagement)
4. DISCOVERABILITY OPTIMIZATION (bio keywords, links, contact visibility)
5. GITHUB ACTIONS SHOWCASE (badges, workflows)
6. BIO VARIATIONS + PIN STRATEGY + TOPIC TAGS
```

**Post-Processing:**
1. Update README with live stats/widgets
2. Apply checklist across pinned repositories
3. Refresh bio and contact details in GitHub settings
4. Reorder pinned repos for narrative flow
5. Announce refreshed profile on LinkedIn/Twitter

---

## 🔵 Low Priority (Future Enhancements)

Apply the same Master Factory delivery rules here—ship runnable code/config/data/docs bundles, follow the startup recipe for set-up, and close each effort with `PROJECT_COMPLETION_CHECKLIST.md`.

- **LOW-001:** Additional Cloud Projects (multi-region DR, service mesh, IAM automation)
- **LOW-002:** Advanced Kubernetes Work (operators, custom controllers, policy engines)
- **LOW-003:** Security Projects (SIEM pipeline, threat detection, pentesting playbooks)
- **LOW-004:** Mobile App for Homelab Management (React Native/Flutter dashboards)
- **LOW-005:** Technical YouTube Channel Scripts (series planning, thumbnails, SEO)

These items are optional and can wait until core portfolio pieces are complete.

---

## 📊 Execution Priority Matrix

```
IMPACT vs EFFORT Grid

High Impact / Low Effort (Do First):
✅ CRIT-001 to CRIT-004 (see Part 1)

High Impact / High Effort (Do Second):
🟡 HIGH-001, HIGH-002, MED-001

Medium Impact / Low Effort (Do Third):
🟢 HIGH-003, MED-006, MED-005

Medium Impact / High Effort (Do Later):
⚪ MED-002, MED-003, MED-004

Low Impact: 🔵 LOW-* backlog
```

---

## 🎯 Recommended Execution Sequence

**Week 1:** Critical foundation (CRIT-001 → CRIT-005)  
**Week 2:** HIGH-001 (AWS Terraform)  
**Week 3:** HIGH-002 (Kubernetes CI/CD)  
**Week 4:** HIGH-003 (Portfolio site), HIGH-004 (Video), MED-006 (GitHub optimization)

**Month 2:** Execute MED-001, MED-002, MED-003 as needed, plus MED-005 blog content.

---

## 📝 Next Document

Proceed to `AI_PROMPT_EXECUTION_FRAMEWORK.md` (Part 3) for:
- Prompt engineering best practices
- Batch processing workflows
- Quality control checklists
- Tool selection guidance
- Time estimation and scheduling
- Prompt library organization tips
- Advanced refinement techniques
