# Portfolio Navigation Guide

Use this quick-reference to digest the 75,000+ words across the Portfolio Master Index deliverables.

## Document Map

| File | Purpose |
|------|---------|
| `Portfolio_Master_Index_CONTINUATION.md` | Homelab deep-dive (Sections 4.1.1–4.1.7). |
| `Portfolio_Master_Index_COMPLETE.md` | Remaining sections 4.1.8–11 (observability, automation, evidence, learning). |
| `Portfolio_Navigation_Guide.md` | Meta-guide plus interview prep workflow (this file). |

## Rapid Interview Prep (1.5 Hours)

1. **Network Architecture (20 min)** – Read Section 4.1.3. Talking point: 5-VLAN zero-trust design blocking lateral movement.
2. **Observability Stack (30 min)** – Read Section 4.1.8. Talking point: 18-minute MTTR via SLO-based alerting/runbooks.
3. **CI/CD Automation (25 min)** – Read Section 4.2.1. Talking point: 80% faster deployments, 0% failure rate.
4. **SLO Alerting & Runbooks (20 min)** – Read Section 4.3.1. Talking point: 67% MTTR reduction with burn-rate alerts.
5. **Disaster Recovery (15 min)** – Revisit Section 4.1.7 for RTO/RPO metrics.

## Top 10 Metrics to Memorize

```
1. $13,005 (97% cost savings vs AWS)
2. 99.8% uptime (target 99.5%)
3. 18-minute average MTTR
4. 0 security incidents in 6 months
5. 1,247 SSH attacks blocked/month
6. Deployments: 2h → 12m (80% faster)
7. 0% deployment failure rate (6 months)
8. 45-minute RTO (target 4h, 87% better)
9. 240+ hours/month saved via automation
10. 67% MTTR improvement (runbooks)
```

## Practice Narratives (Record Yourself)

1. **Homelab Infrastructure (3 min)** – Stress business case (97% savings) + full-stack ownership.
2. **Zero-Trust Security (3 min)** – VPN+MFA, VLANs, 0 exposed admin ports, 1,247 attacks blocked.
3. **CI/CD Pipeline (3 min)** – Multi-stage pipeline, blue-green deploys, zero incidents.
4. **Observability (3 min)** – SLOs, Grafana/Loki, MTTR proof.
5. **Disaster Recovery (3 min)** – 3-2-1 backups, 45-minute RTO, quarterly drills.

## Evidence Checklist

- [ ] Config repo: Terraform modules, Docker Compose, monitoring configs.
- [ ] Screenshots: Grafana dashboards, uptime graphs, diagrams.
- [ ] Architecture diagrams: Network topology, observability, CI/CD, DR flows.
- [ ] Metrics cheat sheet (above) printed or on tablet.
- [ ] Role-specific PDF extracts (SDE, Solutions Architect, SRE).

## Interview Scenario Prompts

| Scenario | Section to Review | Key Hook |
|----------|------------------|----------|
| "Tell me about reliability improvements" | 4.1.8 | MTTR 45m → 18m, SLO burn-rate alerts. |
| "How do you secure infrastructure?" | 4.1.3 & 4.1.5 | Zero-trust VLANs, VPN+MFA, IDS metrics. |
| "Discuss automation impact" | 4.2.1 & 4.1.7 | Deployment + backup automation ROI. |
| "Walk through a DR event" | 4.1.7 | 45-min restoration, runbook steps, drills. |
| "How do you plan learning goals?" | Section 11 | Quarterly roadmap, certifications, metrics. |

## Pre-Interview Checklist

### Must-Have
- [ ] Read priority sections.
- [ ] Memorize metrics.
- [ ] Record/critique five narratives.
- [ ] Publish configs/screenshots to GitHub repo.

### Should-Have
- [ ] Update README/documentation index links.
- [ ] Produce architecture diagrams.
- [ ] Prepare STAR responses (Section 7 references).

### Nice-to-Have
- [ ] Record short walkthrough video.
- [ ] Publish LinkedIn post referencing portfolio.
- [ ] Conduct mock interview focusing on system design.

## Elevator Pitch Template

> “I built a production-grade homelab demonstrating enterprise infrastructure skills—5-VLAN zero-trust security, ZFS storage with DR procedures, comprehensive observability, and CI/CD automation. It delivers 99.8% uptime while saving $13k versus cloud and cutting MTTR to 18 minutes, proving production rigor at any scale.”

## Contact & Distribution

- Include links to both Master Index files in README, DOCUMENTATION_INDEX, and PR summaries.
- For recruiters, share Navigation Guide + role-specific extract PDFs for fast onboarding.

