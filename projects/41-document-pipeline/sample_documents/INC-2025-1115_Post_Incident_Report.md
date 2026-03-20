# INC-2025-1115 Post Incident Report

**Author:** Incident Commander: Taylor Morgan  
**Date:** 2026-01-15  
**Document Type:** Incident Report  

---

## Incident Summary

| Field | Value |
| --- | --- |
| Incident ID | INC-2025-1115 |
| Severity | SEV-1 |
| Start Time | 2025-11-15 14:32 UTC |
| End Time | 2025-11-15 16:08 UTC |
| Duration | 96 minutes |
| Affected Services | Checkout API, Payment Gateway Integration |
| Affected Users | ~12,400 (EU-West region) |
| Incident Commander | Taylor Morgan |
| Status | Resolved — follow-up actions in progress |

## Impact Assessment

The outage affected 12,400 users across the EU-West region between 14:32 and 16:08 UTC on 2025-11-15 (96 minutes total). Checkout and payment processing were unavailable. Estimated revenue impact: $34,000. No data loss occurred. SLA breach of 0.067% for the month.

## Incident Timeline

| Time (UTC) | Event | Actor |
| --- | --- | --- |
| 14:32 | Automated PagerDuty alert fires: checkout-api error rate > 5% (5-min window) | PagerDuty |
| 14:35 | On-call engineer (T. Morgan) acknowledges alert and begins investigation | T. Morgan |
| 14:41 | Identified spike in 502 errors from payment gateway integration service | T. Morgan |
| 14:48 | Incident declared SEV-1; war room opened in #incident-1115 Slack channel | T. Morgan |
| 14:52 | Database team joins — rules out DB as root cause (latency normal) | A. Rivera |
| 15:03 | Identified misconfigured TLS certificate on the payment-gateway reverse proxy (cert expired 2025-11-15 14:29 UTC) | K. Patel |
| 15:11 | New certificate issued via Let's Encrypt and deployed to proxy | K. Patel |
| 15:14 | Partial recovery: error rate drops from 98% to 12% — stale connections still open | T. Morgan |
| 15:22 | Graceful restart of payment-gateway integration pods initiated | T. Morgan |
| 15:31 | Error rate drops to < 1%; checkout functionality confirmed operational | T. Morgan |
| 15:45 | Extended monitoring window begins; all metrics within normal range | T. Morgan |
| 16:08 | Incident resolved; all-clear communicated to stakeholders | T. Morgan |
| 16:30 | Post-incident review meeting scheduled for 2025-11-18 | T. Morgan |
| 2025-11-18 | Post-incident review conducted; this report drafted | Full IR Team |
| 2026-01-15 | Follow-up action items reviewed; 3 of 5 complete | Platform Team |

## Root Cause Analysis

The TLS certificate for the payment-gateway reverse proxy (Nginx) expired at 14:29 UTC on 2025-11-15. The certificate had been provisioned manually 90 days prior and was not enrolled in the automated Let's Encrypt renewal process. When the certificate expired, Nginx rejected all inbound TLS connections from the checkout API, causing 502 Bad Gateway errors. The manual provisioning process predated the automated renewal tooling and was not captured in the certificate inventory.

## Contributing Factors

- Manual TLS certificate provisioning bypassed the automated renewal pipeline
- Certificate inventory (certificates.yaml) did not include reverse proxy certificates — only application-layer certs
- Monitoring alert for certificate expiry was configured on port 443 of the public endpoint, not the internal proxy; the internal proxy cert was not monitored
- On-call runbook for 502 errors did not include TLS certificate checks as a diagnostic step
- The payment gateway proxy was provisioned by a contractor in Q2 2025 and ownership was not formally transferred to the platform team

## Immediate Remediation Actions

1. **Issue and deploy replacement TLS certificate**
   Let's Encrypt certificate issued and deployed to Nginx proxy at 15:11 UTC.
2. **Graceful restart of integration pods**
   kubectl rollout restart deployment/payment-gateway-integration -n production at 15:22 UTC.
3. **Verify checkout end-to-end**
   Smoke test suite (make smoke-test) run at 15:35 UTC — all 47 tests passed.

## Follow-Up Action Items

| Action | Owner | Due Date | Priority |
| --- | --- | --- | --- |
| Enrol all reverse proxy certificates in automated Let's Encrypt renewal | K. Patel | 2025-12-01 | P1 |
| Audit certificate inventory and add internal proxy certs | K. Patel | 2025-11-30 | P1 |
| Add Prometheus alert for certificates expiring within 14 days (all internal endpoints) | Platform Team | 2025-12-07 | P1 |
| Update 502 on-call runbook to include TLS cert expiry checks | T. Morgan | 2025-11-22 | P2 |
| Formalise service ownership transfer process for contractor-provisioned resources | Engineering Manager | 2026-01-31 | P2 |

## Lessons Learned

- Manual infrastructure provisioning must be immediately captured in automation tooling and inventories — no exceptions.
- Certificate monitoring must cover all TLS endpoints, including internal proxies, load balancers, and service meshes — not just public-facing URLs.
- On-call runbooks require a TLS/certificate health check section as a standard diagnostic step for any 502/503 scenario.
- Service ownership must be formally transferred and documented before a contractor's engagement ends.
- A 14-day advance warning for expiring certificates provides sufficient lead time; current 3-day alert (for monitored certs) is insufficient.

---

*Generated by Document Pipeline v1.0 | 2026-01-15*
