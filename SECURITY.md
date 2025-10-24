# Security Overview

This portfolio repository captures the processes, documentation, and representative evidence used to secure the showcased projects. The goals are to demonstrate a mature security posture while keeping sensitive artifacts out of the public export.

## Security Governance
- Ownership for security policies, vulnerability management, and incident response sits with the **Security & Reliability** working group (primary contact: `security@samsjackson.dev`).
- All changes to infrastructure or application code require code review, automated testing, and adherence to the documented change management checklist before promotion to production-like environments.

## Security Testing
- **Security test plan:** Review the repeatable verification activities, tooling, and cadences that are applied across projects in [`documentation/security/security-test-plan.md`](./documentation/security/security-test-plan.md).
- **Penetration testing evidence:** Sanitized summaries are provided in [`documentation/security/pentest-reports/`](./documentation/security/pentest-reports/). Raw reports remain access-controlled; follow the instructions in that directory to request time-bound access to full findings and remediation tracking assets.

## Reporting an Issue
To report a suspected vulnerability or security incident, email `security@samsjackson.dev` with the affected project, reproduction steps, and any relevant evidence. Public disclosure is requested to follow a 90-day coordinated timeline unless immediate risk warrants faster action.
