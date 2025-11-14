# Portfolio Navigation Guide

The Portfolio Master Index documents are intentionally dense, so this guide acts as a map for recruiters, interviewers, and new contributors who need fast access to the right talking points. Each section references the corresponding numbering used in the **Portfolio_Master_Index_COMPLETE.md** and **Portfolio_Master_Index_CONTINUATION.md** files so you can jump between summaries and the full write-ups.

## Table of Contents
1. [Rapid Interview Prep (1.5 Hours)](#rapid-interview-prep-15-hours)
2. [24-Hour Deep Dive](#24-hour-deep-dive)
3. [Top 10 Metrics to Memorize](#top-10-metrics-to-memorize)
4. [Navigation Patterns by Stakeholder](#navigation-patterns-by-stakeholder)
5. [Artifact Cross-Reference](#artifact-cross-reference)

---

## Rapid Interview Prep (1.5 Hours)

Spend ninety minutes reviewing the three highest-impact areas before a technical conversation:

1. **Network Architecture (20 min)** – Read Section **4.1.3** in the complete index. Talking point: 5-VLAN zero-trust design blocks lateral movement by isolating prod, staging, lab, management, and guest networks with ACL enforcement at the pfSense core.
2. **Observability Stack (30 min)** – Read Section **4.1.8**. Talking point: 15-minute MTTR via SLO-based alerting, Grafana runbooks, and distributed tracing that ties user journeys directly to service health.
3. **Automation Pipeline (20 min)** – Read Section **4.2.4**. Talking point: 480 hours/year saved with GitHub Actions + Ansible GitOps workflows for homelab, Kubernetes, and Terraform estate.
4. **Resilience Playbooks (20 min)** – Read Section **4.3.1**. Talking point: Multi-tier backup plus tabletop-tested incident response covering ransomware, certificate leaks, and S3 equivalence restores.

**Lightning Refresh (10 min)** – Skim Section **4.1.8** tables again to reiterate the 15-minute MTTR story and the role of SLO burn-rate alerts so the number stays top-of-mind.

---

## 24-Hour Deep Dive

When preparing a portfolio review or executive readout, block off one day and focus on these phases:

### Phase 1: Infrastructure Foundations (Hours 0-6)
- Section **4.1.1** – Hardware bill of materials, 95% cost savings versus AWS ($13,005 saved on a $13,680 three-year TCO).
- Section **4.1.3** – Logical diagrams and VLAN segmentation strategy. Capture the security rationale for the interview deck.

### Phase 2: Observability + Operations (Hours 6-12)
- Section **4.1.8** – Dive into the Prometheus, Loki, Tempo, and Grafana configuration. The table on page 38 highlights the 15-minute MTTR trend line.
- Section **4.2.2** – Incident command structure tied to MTTR and MTTD measurements.

### Phase 3: Automation & Learning Loop (Hours 12-18)
- Section **4.2.4** – GitHub Actions pipelines, self-healing Ansible jobs, and Terraform drift detection.
- Section **5.1** – Continuous learning roadmap linking certifications, research spikes, and backlog grooming.

### Phase 4: Story Synthesis (Hours 18-24)
- Build your narrative deck by combining the MTTR chart, the 95% cost comparison, and the automation ROI graphic from Appendix B.
- Use the stakeholder navigation table below to decide which appendices to append to the final presentation.

---

## Top 10 Metrics to Memorize

```
1. $13,005 (95% cost savings vs AWS)
2. 15-minute MTTR (SLO-driven alerting with runbooks)
3. 99.8% uptime across critical homelab services
4. 480 hours/year manual toil removed through automation
5. 92% CIS hardening coverage across Linux estate
6. 45-minute → 12-minute certificate rotation time
7. 10+ long-running services backed by GitOps workflows
8. 30 TB effective ZFS capacity with 3-2-1 replication
9. 15 SLOs instrumented with shared dashboards
10. 12 documented incident simulations in the last year
```

Keep the MTTR number bolded on your notepad; every follow-up question about operations flows naturally to the SLO architecture or the on-call runbooks. Likewise, the cost-savings metric turns into a conversation about financial stewardship, rack layout, and the hybrid-cloud translation story.

---

## Navigation Patterns by Stakeholder

### Recruiters / Technical Sourcers
- Open **Portfolio_Master_Index_COMPLETE.md** and read Sections 2 through 4 for a big-picture summary.
- Jump to this guide’s [Rapid Interview Prep](#rapid-interview-prep-15-hours) section for elevator pitches.
- Copy the MTTR and cost-savings bullets directly into outreach messages.

### Engineering Managers
- Use the table in **Portfolio_Master_Index_CONTINUATION.md Section 6.2** to correlate projects, SLOs, and automation ownership.
- Reference the artifact cross-reference below to pair a talking point with source proof (dashboards, Terraform repos, or runbooks).

### Platform / SRE Engineers
- Focus on Sections **4.1.8** and **4.2.2** in the complete index for a deep look at observability and incident response.
- Follow links to Grafana dashboards and Alertmanager configs when you need raw data backing the 15-minute MTTR.

### Security & Compliance Leaders
- Reference Sections **4.3.1** and **4.3.4** for the layered defense model, tabletop exercises, and audit evidence.
- Use the cost-optimization appendix in the continuation file to show fiduciary discipline alongside security rigor.

---

## Artifact Cross-Reference

| Focus Area            | Key Artifact                                      | Location/Notes |
|-----------------------|---------------------------------------------------|----------------|
| Network segmentation  | Section 4.1.3 diagrams                             | Portfolio_Master_Index_COMPLETE.md |
| Observability stack   | Section 4.1.8 metrics tables                       | Portfolio_Master_Index_COMPLETE.md (MTTR = 15 min) |
| Automation workflows  | Section 4.2.4 pipeline blueprints                   | Portfolio_Master_Index_COMPLETE.md |
| Cost optimization     | Section 6.1 cost tables                            | Portfolio_Master_Index_CONTINUATION.md (95% savings) |
| AI prompt playbooks   | Critical/High/Medium prompt sets                    | AI_PROMPT_LIST_FOR_GAPS.md |

Use this grid as a checklist when assembling interview packets. Each talking point should include the source section reference, a screenshot or diagram when possible, and the correct metric (15-minute MTTR, 95% cost savings) repeated verbatim for consistency.
