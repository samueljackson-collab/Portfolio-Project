# Project Charter — Customer Portal v2.0

**Project ID:** PRJ-2026-007
**Date:** 2026-01-15
**Version:** 1.0 (Approved)

---

## 1. Project Overview

| Field | Detail |
|-------|--------|
| **Project Name** | Customer Portal v2.0 |
| **Sponsor** | VP of Product |
| **Project Manager** | Sarah Chen |
| **Start Date** | 2026-02-03 |
| **End Date** | 2026-05-30 |
| **Budget** | $145,000 |
| **Priority** | High |

## 2. Problem Statement

The existing customer portal (v1.3) was built in 2021 on a deprecated framework and cannot
support mobile-first design, SSO integration, or the self-service features customers have requested
in Q3/Q4 2025 satisfaction surveys. Customers rate portal usability at 2.8/5.0 (target: 4.0+).

## 3. Objectives

1. Rebuild portal on React + FastAPI with WCAG 2.1 AA accessibility compliance
2. Implement SSO (SAML/OIDC) with corporate identity provider
3. Deliver 5 new self-service features: order tracking, invoice download, support tickets, profile management, usage dashboards
4. Achieve mobile-first responsive design (target: > 60% mobile usage)
5. Reduce customer support ticket volume by 30% (baseline: 450/month)

## 4. Scope

### In Scope
- New React frontend (replaces AngularJS v1.5)
- FastAPI backend with OpenAPI documentation
- SSO integration (Okta SAML)
- Customer data migration from v1.3 database
- 5 self-service features listed above

### Out of Scope
- Payment processing changes (separate PCI project)
- Admin portal (separate roadmap item)
- Mobile native apps (web-first; native apps Q3 2026)

## 5. Success Criteria

| Metric | Baseline | Target | Measurement |
|--------|---------|--------|-------------|
| Portal usability score | 2.8/5.0 | ≥ 4.0/5.0 | Quarterly NPS survey |
| Support ticket volume | 450/month | ≤ 315/month (–30%) | Zendesk monthly report |
| Mobile session share | 38% | ≥ 60% | Google Analytics |
| Page load time (p95) | 4.2s | ≤ 1.5s | Synthetic monitoring |
| SSO adoption | 0% | 90% of active users | Auth logs |

## 6. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Data migration complexity | Medium | High | Run parallel for 4 weeks; rollback plan |
| SSO integration delays | Low | Medium | Start Okta engagement in week 1 |
| Scope creep | High | Medium | Strict change control; PM owns backlog |
| Resource availability | Low | High | Dedicated team; no context switching |

## 7. Approvals

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Project Sponsor | VP of Product | ✅ Approved | 2026-01-15 |
| IT Director | James Okoye | ✅ Approved | 2026-01-15 |
| Security (CISO Office) | SOC Lead | ✅ Approved | 2026-01-15 |
| Project Manager | Sarah Chen | ✅ Acknowledged | 2026-01-15 |
