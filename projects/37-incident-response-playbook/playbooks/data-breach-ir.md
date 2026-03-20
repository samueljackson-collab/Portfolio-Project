# Data Breach Incident Response Playbook

**Playbook ID:** IRP-003
**Version:** 1.2
**Last Updated:** 2026-01-10

---

## Scope

Response to confirmed or suspected unauthorised access to, or exfiltration of, personally identifiable
information (PII), protected health information (PHI), payment card data (PCI), or confidential
business data.

---

## Regulatory Notification Deadlines

| Regulation | Deadline | Scope |
|-----------|---------|-------|
| GDPR (EU) | **72 hours** from discovery | EU resident data |
| HIPAA (US) | **60 days** from discovery | PHI/ePHI |
| CCPA (California) | **Most expedient** + reasonable time | CA resident data |
| PCI DSS | **Immediately** to acquiring bank | Payment card data |
| SEC (US public co.) | **4 business days** | Material cybersecurity incident |
| State breach laws | Varies (30–90 days) | State-specific requirements |

---

## Phase 1 — Identification and Scoping

### Data Classification Assessment

```
CRITICAL (notify within 72 hours):
  - SSN, passport, driver's licence numbers
  - Payment card numbers (PAN, CVV, expiry)
  - PHI / medical records
  - Authentication credentials (passwords, tokens)

HIGH (notify within 7 days):
  - Employee PII (salary, performance, HR records)
  - Customer contact data + purchase history
  - Proprietary source code or trade secrets

MEDIUM (notify within 30 days):
  - Internal email / calendar data
  - Non-customer business data
```

### Scope Questions

1. What data was accessed? (type, volume, time window)
2. Is the attacker still in the environment? (ongoing vs. historical)
3. Was data exfiltrated or only accessed in-place?
4. Which systems/databases contained the data?
5. How many individuals are affected?

---

## Phase 2 — Legal and Compliance Notification

### Internal Notification (within 1 hour of confirmation)

1. CISO
2. Legal Counsel
3. Chief Privacy Officer (CPO) or DPO (GDPR)
4. CEO / Executive Team
5. HR (if employee data involved)

### External Notification Workflow

```
Breach Confirmed
       │
       ├──► Legal determines regulatory scope
       │
       ├──► GDPR? → DPA notification within 72h
       │
       ├──► HIPAA? → HHS notification + media (if >500)
       │
       ├──► PCI? → Immediate acquirer notification
       │
       └──► Affected individuals notification
            (content: what happened, data involved,
             actions taken, protective steps, contact)
```

---

## Phase 3 — Containment and Eradication

- [ ] Revoke all access for compromised accounts
- [ ] Patch or take offline the exploited system
- [ ] Rotate database credentials
- [ ] Audit all access logs for the affected data store (last 90 days)
- [ ] Engage DLP tools to identify additional exfiltration paths

---

## Phase 4 — Recovery

- [ ] Systems restored from clean backup
- [ ] Enhanced monitoring on all data stores
- [ ] Data loss prevention (DLP) policy tightened
- [ ] Encryption at rest verified for all sensitive data stores
- [ ] Credit monitoring offered to affected individuals (if PII)

---

## Phase 5 — Lessons Learned

- PIR completed within 10 business days
- Regulatory submissions reviewed by legal before filing
- Insurance claim filed if applicable
- Board briefing prepared by CISO
