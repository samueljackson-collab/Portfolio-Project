# Playbook Phase 1 — Project Intake

**Version**: 2.1
**Owner**: Programme Management Office (PMO)
**Last Updated**: 2026-01-10
**Review Cycle**: Quarterly

---

## 1. Purpose and Scope

The project intake process establishes a structured gate through which all new IT work must pass before resources are committed. It ensures that every project is clearly defined, properly justified, aligned with business strategy, and approved by the correct stakeholders before design or development begins.

**In Scope**: All new IT projects, major enhancements (>40 hours estimated effort), and third-party software evaluations.
**Out of Scope**: Bug fixes, routine maintenance tasks, and operational changes covered by the Change Management process.

---

## 2. Intake Process Overview

```
Business Request
     │
     ▼
[2.1] Intake Form Submission (Requestor)
     │
     ▼
[2.2] Initial Triage (PMO) — 2 business days
     │
     ├── Duplicate/out-of-scope → Rejected (with explanation)
     │
     ▼
[2.3] Classification & Scoring
     │
     ▼
[2.4] Stakeholder Identification
     │
     ▼
[2.5] Go/No-Go Decision (Steering Committee)
     │
     ├── No-Go → Deferred or Rejected (with rationale)
     │
     ▼
[2.6] Project Charter Creation → Phase 2: Design
```

---

## 3. Intake Form Template

All fields must be completed. Incomplete forms will be returned within 1 business day.

| Field | Description |
|-------|-------------|
| **Project Title** | Short, descriptive title (max 60 characters) |
| **Requestor Name** | Full name of the person submitting the request |
| **Requestor Department** | Department or business unit |
| **Executive Sponsor** | VP or Director level sponsor who owns the budget |
| **Date Submitted** | ISO date (YYYY-MM-DD) |
| **Requested Start Date** | Earliest acceptable project start |
| **Requested Completion Date** | Business deadline (hard or soft — specify) |
| **Business Problem Statement** | 2–5 sentences: what problem is being solved, and what happens if it is not solved? |
| **Proposed Solution** | High-level description of the proposed approach |
| **Business Justification** | ROI narrative, regulatory requirement, or strategic alignment |
| **Success Criteria** | 3–5 measurable outcomes that define project success |
| **Known Constraints** | Budget cap, technology restrictions, compliance requirements |
| **Assumptions** | List assumptions the estimate is based on |
| **Dependencies** | Other projects, teams, or systems this depends on |
| **Risks (Initial)** | Top 3 anticipated risks at intake |
| **Budget Estimate** | Rough order of magnitude (ROM) estimate in USD |
| **Resource Requirements** | Team size, specialist skills needed |
| **Impacted Systems** | List all systems that will be modified or integrated |
| **Data Classification** | Public / Internal / Confidential / Restricted |
| **Regulatory/Compliance** | GDPR, SOC 2, HIPAA, PCI-DSS, or N/A |

---

## 4. Worked Example — Completed Intake Form

### Project Intake: E-commerce Platform Upgrade Q1 2026

| Field | Value |
|-------|-------|
| **Project Title** | E-commerce Platform Upgrade — Q1 2026 |
| **Requestor Name** | Sarah Chen, Director of Digital Commerce |
| **Requestor Department** | Digital Commerce |
| **Executive Sponsor** | Marcus Webb, VP Technology |
| **Date Submitted** | 2026-01-08 |
| **Requested Start Date** | 2026-02-01 |
| **Requested Completion Date** | 2026-04-30 (soft) |
| **Business Problem Statement** | The current Magento 2.3 platform is approaching end-of-life in June 2026. Security patches will no longer be released. The checkout conversion rate is 2.1% versus the industry average of 3.8%. Page load times average 4.2 seconds on mobile, causing an estimated 28% cart abandonment. Failure to upgrade will expose the company to security vulnerabilities and continued revenue loss. |
| **Proposed Solution** | Migrate to Shopify Plus with custom headless front-end (Next.js). Retain existing product catalogue and order history. Integrate with existing Salesforce CRM and NetSuite ERP. Implement A/B testing framework for conversion optimisation. |
| **Business Justification** | Projected increase in checkout conversion from 2.1% to 3.5% (conservative) adds ~$180K annual revenue at current traffic volumes. EOL platform poses critical security risk. Reduced operational overhead: estimated $35K/year savings in hosting and maintenance. Total 3-year NPV: $412,000. |
| **Success Criteria** | 1. Mobile page load < 2.0 seconds (p75) by go-live. 2. Checkout conversion rate ≥ 3.2% within 60 days post-launch. 3. Zero security vulnerabilities rated Critical or High in first 90 days. 4. 100% product catalogue migrated with zero data loss. 5. CRM and ERP integrations passing smoke tests before go-live. |
| **Known Constraints** | Budget cap: $127,500. Shopify Plus plan required (pre-approved). Cannot go live within 2 weeks of Black Friday (November). Existing payment gateway (Stripe) must be retained. |
| **Assumptions** | Product catalogue (~4,200 SKUs) can be migrated via CSV export. Salesforce CRM API is available and documented. Internal developer capacity: 2 FTE for 12 weeks. |
| **Dependencies** | Salesforce Admin team to provide API credentials (by 2026-02-08). NetSuite ERP upgrade (Project PRJ-2025-041) must complete before integration work begins. Legal review of updated Terms & Conditions (3-week lead time). |
| **Risks (Initial)** | 1. Data migration complexity (Medium likelihood, High impact) — mitigate with pilot migration sprint. 2. Third-party integration delays from Salesforce team (Medium/Medium). 3. Scope creep from marketing requests for new features (High likelihood, Medium impact) — strict change control. |
| **Budget Estimate** | $127,500 ROM (±20%) |
| **Resource Requirements** | 1 x Project Manager (0.5 FTE), 2 x Full-stack Developers (1.0 FTE each), 1 x QA Engineer (0.5 FTE), 1 x UX Designer (0.3 FTE) |
| **Impacted Systems** | Magento 2.3 (legacy), Shopify Plus (new), Salesforce CRM, NetSuite ERP, Stripe, CloudFlare CDN, Google Analytics 4 |
| **Data Classification** | Confidential (customer PII, order history) |
| **Regulatory/Compliance** | PCI-DSS (payment card data), GDPR (EU customer data) |

---

## 5. Project Classification Matrix

Score the project using Priority × Effort to determine the intake stream.

### Priority Score (1–5)
| Score | Criteria |
|-------|----------|
| 5 | Legal/regulatory mandate or active security incident |
| 4 | Direct revenue impact > $100K/year or executive directive |
| 3 | Operational efficiency gain > $50K/year or significant user pain |
| 2 | Improves process but limited quantified impact |
| 1 | Nice-to-have, no hard business driver |

### Effort Score (1–5)
| Score | Estimated Effort |
|-------|-----------------|
| 1 | < 40 hours |
| 2 | 40–200 hours (1–5 weeks FTE) |
| 3 | 200–800 hours (1–4 months FTE) |
| 4 | 800–3,200 hours (4–16 months FTE) |
| 5 | > 3,200 hours or multi-team programme |

### Classification Matrix

|                | Effort 1 (XS) | Effort 2 (S) | Effort 3 (M) | Effort 4 (L) | Effort 5 (XL) |
|----------------|---------------|--------------|--------------|--------------|----------------|
| **Priority 5** | Expedite      | Expedite     | Standard     | Standard     | Programme      |
| **Priority 4** | Expedite      | Standard     | Standard     | Programme    | Programme      |
| **Priority 3** | Standard      | Standard     | Standard     | Deferred     | Deferred       |
| **Priority 2** | Standard      | Deferred     | Deferred     | Rejected     | Rejected       |
| **Priority 1** | Deferred      | Rejected     | Rejected     | Rejected     | Rejected       |

**E-commerce Platform Upgrade**: Priority 4, Effort 3 → **Standard** intake stream.

### Intake Stream Definitions
- **Expedite**: Bypass standard queue, assigned within 24 hours, weekly steering updates.
- **Standard**: Normal queue, assigned within 5 business days, fortnightly steering updates.
- **Programme**: Escalated to Programme Board, requires formal business case document.
- **Deferred**: Logged in backlog for next quarterly prioritisation review.
- **Rejected**: Closed with documented rationale, requestor notified.

---

## 6. Stakeholder Identification Worksheet

Complete this for every project that passes initial triage.

| Stakeholder | Role | Interest | Influence | Engagement Strategy |
|-------------|------|----------|-----------|---------------------|
| Executive Sponsor | Owns budget and final authority | High | High | Monthly steering updates, escalation path |
| Project Manager | Day-to-day delivery accountability | High | High | Daily standups, weekly status reports |
| Business Requestor | Defines requirements, accepts deliverables | High | Medium | Sprint reviews, UAT participation |
| IT Operations | Receives and operates the delivered system | Medium | High | Architecture review, runbook sign-off |
| Security Team | Reviews security posture of new system | Medium | High | Security review gates, pen test sign-off |
| Legal/Compliance | Ensures regulatory compliance | Low-Medium | High | Review at design phase and pre-launch |
| End Users | Use the delivered system daily | High | Low | User research, UAT, feedback surveys |
| Finance | Tracks budget and approves expenditure | Low | High | Monthly budget reports |

**E-commerce Platform Upgrade — Stakeholders:**

| Stakeholder | Name | Role | Engagement |
|-------------|------|------|-----------|
| Executive Sponsor | Marcus Webb | VP Technology | Monthly steering |
| Business Owner | Sarah Chen | Director, Digital Commerce | Sprint reviews |
| Project Manager | Alex Patel | Senior PM | Daily |
| Lead Developer | Jordan Kim | Full-stack Lead | Daily |
| QA Engineer | Priya Nair | Senior QA | Daily |
| Security Review | Chris Monroe | InfoSec Lead | Gate reviews |
| Legal Compliance | Avery Stone | Privacy Counsel | Design phase + pre-launch |

---

## 7. Go/No-Go Criteria Checklist

All items must be checked YES before the project proceeds to Phase 2 (Design).

### Mandatory (all must be YES)
- [ ] Intake form is fully completed and signed off by Executive Sponsor
- [ ] Project has a unique identifier assigned (format: PRJ-YYYY-NNN)
- [ ] Budget has been confirmed and approved by Finance
- [ ] Project does not duplicate an existing active project
- [ ] Resource availability confirmed for requested start date
- [ ] Legal/compliance requirements identified (or confirmed N/A)
- [ ] Data classification has been assigned
- [ ] Security team has been notified and agreed on review timeline

### Recommended (failure requires documented waiver)
- [ ] Impacted system owners have been consulted
- [ ] ROM estimate is within ±30% confidence (or wider range is documented)
- [ ] At least 3 measurable success criteria have been defined
- [ ] Rollback or exit criteria have been defined
- [ ] Project has been classified using the Priority × Effort matrix

### E-commerce Upgrade — Go/No-Go Decision
| Item | Status | Notes |
|------|--------|-------|
| Intake form fully completed | YES | Signed by Marcus Webb 2026-01-09 |
| Unique ID assigned | YES | PRJ-2026-008 |
| Budget confirmed | YES | $127,500 approved 2026-01-10 |
| No duplication | YES | No other e-commerce projects active |
| Resource availability | YES | Dev team confirmed available 2026-02-01 |
| Compliance identified | YES | PCI-DSS + GDPR |
| Data classification | YES | Confidential |
| Security notified | YES | Chris Monroe acknowledged 2026-01-09 |
| **GO/NO-GO Decision** | **GO** | Approved by steering 2026-01-12 |

---

## 8. Intake Outputs

Upon successful Go decision, the following artefacts are created:

1. **Project ID**: Assigned and logged in the project register
2. **Project Charter** (template: `examples/sample-project-charter.md`)
3. **Stakeholder Register**: Populated worksheet
4. **Risk Register**: Initial risks captured from intake form
5. **Backlog**: Initial epic-level requirements
6. **Phase Transition**: Handoff to Phase 2 (Design & Architecture)

**Next Phase**: [02-design-architecture.md](02-design-architecture.md)
