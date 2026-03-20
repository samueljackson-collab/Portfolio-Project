# Incident Escalation Matrix

**Version:** 2.0 | **Last Updated:** 2026-01-10

---

## Severity Definitions

| Severity | Label | Description | Examples |
|----------|-------|-------------|---------|
| **P1** | Critical | Active compromise with business-wide impact | Ransomware spreading, DC compromise, customer data breach confirmed |
| **P2** | High | Significant impact on systems or data, contained | Single server compromised, phishing with credential theft |
| **P3** | Medium | Limited impact, no data loss | Malware on isolated endpoint, failed intrusion attempt |
| **P4** | Low | Minimal impact, policy violation | Suspicious email (not clicked), port scan detected |

---

## Notification Timeline by Severity

| Severity | Analyst | SOC Lead | CISO | Legal | CEO/Board | PR/Comms |
|----------|---------|----------|------|-------|-----------|---------|
| P1 | Immediate | 5 min | 15 min | 30 min | 1 hour | 2 hours |
| P2 | Immediate | 15 min | 1 hour | 2 hours | If data breach | If data breach |
| P3 | Immediate | 1 hour | Next business day | If data involved | No | No |
| P4 | Immediate | Next shift | Weekly summary | No | No | No |

---

## On-Call Rotation

| Role | Primary | Backup | Out-of-Band |
|------|---------|--------|-------------|
| SOC Analyst (24/7) | Rotating roster | Senior analyst | SOC Slack + PagerDuty |
| SOC Lead | Primary on-call | Backup on-call | PagerDuty P1/P2 |
| CISO | Direct mobile | Deputy CISO | Signal |
| Legal | General Counsel | Outside counsel retainer | Mobile |
| IR Retainer | IR Firm 24/7 line | — | +1-800-XXX-0001 |

---

## P1 Bridge Call Protocol

1. **SOC Analyst** opens bridge call (Zoom war room link in wiki)
2. **SOC Lead** assumes Incident Commander (IC) role
3. **IC** assigns: Scribe, Technical Lead, Comms Lead
4. **Bridge call cadence:** Status update every 30 minutes
5. **Decision log** maintained in real-time by Scribe
6. **Escalate to CEO** if: ransomware confirmed / customer data at risk / media inquiry received

---

## SLAs

| Metric | P1 | P2 | P3 | P4 |
|--------|----|----|----|----|
| Acknowledgement | 5 min | 15 min | 30 min | 4 hours |
| Containment | 1 hour | 4 hours | 24 hours | 72 hours |
| Eradication | 4 hours | 24 hours | 72 hours | 1 week |
| Recovery | 8 hours | 48 hours | 1 week | 2 weeks |
| PIR completion | 5 days | 10 days | 15 days | 30 days |
