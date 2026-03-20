# Phishing Incident Response Playbook

**Playbook ID:** IRP-002
**Version:** 1.4
**Last Updated:** 2026-01-10

---

## Scope

Response to phishing attacks targeting corporate users via email, SMS (smishing), voice (vishing),
or adversary-in-the-middle (AiTM) credential harvesting.

---

## Phase 1 — Identification

### Detection Triggers

```
HIGH-CONFIDENCE:
  - User reports suspicious email with credential harvest link
  - Email gateway (Defender, Proofpoint) quarantined bulk campaign
  - Azure AD / Okta: impossible travel login or new country MFA prompt
  - AiTM token theft: session cookie replayed from unexpected IP

MEDIUM-CONFIDENCE:
  - Multiple password reset requests in short window
  - External email with lookalike sender domain
  - Link to non-corporate document sharing service
```

### Triage Questions

1. Did the user **click** the link? (Yes/No/Unknown)
2. Did the user **enter credentials**? (Yes/No/Unknown)
3. Did the user **approve an MFA prompt** they did not initiate?
4. What is the sender address and originating IP?
5. How many users received the same email?

---

## Phase 2 — Containment

```bash
# Revoke all active sessions for compromised user (Azure AD / M365)
# PowerShell:
Revoke-AzureADUserAllRefreshToken -ObjectId <user_object_id>

# Or via Graph API:
POST https://graph.microsoft.com/v1.0/users/{id}/revokeSignInSessions

# Block sender domain at email gateway
# Add to tenant block list:
New-TenantAllowBlockListItems -ListType Sender -Block -Entries "malicious-domain.com"
```

### Containment Checklist

- [ ] Compromised user account disabled or credentials reset
- [ ] All active sessions revoked
- [ ] MFA re-enrolled on secure device
- [ ] Phishing email purged from all mailboxes (Purge-Content / Exchange search)
- [ ] Sender domain/IP blocked at gateway
- [ ] Link/URL blocked at proxy/DNS filter

---

## Phase 3 — Investigation

- Review email headers (SPF/DKIM/DMARC pass/fail)
- Analyse link destination — credential phish, malware dropper, or OAuth consent phish?
- Check Azure AD sign-in logs for successful logins from harvested credentials
- Review email audit logs — has attacker set mail forwarding rules?
- Check OAuth apps — has attacker granted a malicious app access?

---

## Phase 4 — Recovery and Hardening

- [ ] Enforce phishing-resistant MFA (FIDO2/hardware key) for affected accounts
- [ ] Review and revoke suspicious OAuth application grants
- [ ] Remove attacker-created inbox rules
- [ ] User security awareness refresher
- [ ] Add phishing domain to threat intel feeds

---

## Metrics

| Metric | Target |
|--------|--------|
| Time to report (user → SOC) | < 30 min |
| Time to quarantine campaign | < 1 hour |
| Time to revoke compromised sessions | < 2 hours |
| User click-through rate (training baseline) | < 5% |
