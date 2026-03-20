# Communication Templates

## 1. Initial Internal Alert (P1/P2)

**Subject:** [P1 INCIDENT] Potential Ransomware Detected — INC-2026-XXXX

```
Team,

A potential [INCIDENT TYPE] has been detected affecting [SCOPE].

Incident ID: INC-2026-XXXX
Detected: [DATETIME UTC]
Affected systems: [LIST]
Current status: INVESTIGATION IN PROGRESS

The SOC team is actively responding. A bridge call is open at [ZOOM LINK].

IC: [NAME]
Next update: [DATETIME]

All teams: Do NOT shutdown, reboot, or modify affected systems without SOC approval.
```

---

## 2. Executive Briefing (P1 — first 60 min)

**Subject:** Cybersecurity Incident Update — [DATE]

```
Executive Summary:

At approximately [TIME], our security team detected [BRIEF DESCRIPTION].

Current Status: [CONTAINED / INVESTIGATION ONGOING / RECOVERY IN PROGRESS]

Business Impact:
  - Systems affected: [NUMBER AND NAMES]
  - Data at risk: [YES/NO — specify type if yes]
  - Customer impact: [YES/NO/UNKNOWN]
  - Estimated downtime: [ESTIMATE]

Actions Taken:
  1. [Action 1]
  2. [Action 2]

Next Steps:
  - [Next action with owner and ETA]

Next update: [DATETIME]
Contact: [CISO NAME] — [PHONE]
```

---

## 3. Customer Notification (Data Breach — GDPR-compliant)

**Subject:** Important Security Notice Regarding Your Account

```
Dear [CUSTOMER NAME],

We are writing to inform you of a security incident that may have affected
your account information.

What Happened:
On [DATE], we discovered that [BRIEF DESCRIPTION OF INCIDENT] resulted in
unauthorised access to [DESCRIPTION OF DATA].

What Information Was Involved:
[LIST OF DATA TYPES: name, email, encrypted password, etc.]

What We Are Doing:
- [Action 1]
- [Action 2]
- [Action 3]

What You Can Do:
1. Change your password immediately at [URL]
2. Enable two-factor authentication
3. Monitor your accounts for suspicious activity
4. [Additional steps if financial data involved]

For questions, contact our dedicated support team at:
  Email: security-incident@[domain]
  Phone: [NUMBER] (available [HOURS])

We sincerely apologise for any inconvenience this may cause.

[COMPANY] Security Team
```

---

## 4. Regulatory Notification (GDPR — Article 33)

For use by Legal/DPO only. Submit to relevant Data Protection Authority within 72 hours.

```
To: [Supervisory Authority name and contact]
From: [Data Controller name, address, DPO contact]
Date: [DATE/TIME UTC]

Article 33 Notification — Personal Data Breach

1. Nature of breach: [access / disclosure / loss / destruction]
2. Categories of data subjects affected: [customers / employees / other]
3. Categories and approximate number of records: [NUMBER]
4. Name and contact of DPO: [NAME, EMAIL, PHONE]
5. Likely consequences: [DESCRIBE]
6. Measures taken or proposed: [DESCRIBE]

Ref: GDPR Article 33 — Notification obligation to supervisory authority
```
