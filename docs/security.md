# Security Program Overview

The security posture for the portfolio is built on layered controls, threat modeling, and regular verification. Visual artifacts are tracked under `docs/assets/` to capture evolving security designs.

## Threat Modeling

![Threat Model](assets/security-threat-model.drawio)

The threat model diagram outlines:

- **Actors** – Administrators, contributors, and anonymous visitors.
- **Targets** – Infrastructure services, CI/CD pipelines, documentation artifacts.
- **Trust Boundaries** – Network zones, authentication tiers, and data classification boundaries.
- **Mitigations** – MFA, role-based access control, encrypted backups, and continuous monitoring.

## Defense-in-Depth Layers

![Defense Layers](assets/security-defense-layers.drawio)

Security controls stack across layers:

1. **Network** – VLAN segmentation, VPN ingress, firewall policies.
2. **Identity & Access** – Centralized directory, least-privilege role assignments, just-in-time access.
3. **Application & Automation** – Secret scanning, dependency audits, and signed artifacts.
4. **Operations** – Runbooks for incident response, backup/restore drills, logging retention.

## Verification Activities

- **Automated Scanning** – Weekly secret scan jobs, static analysis on every merge request.
- **Manual Reviews** – Quarterly threat model refresh using the diagrams above.
- **Disaster Recovery Tests** – Semi-annual restore exercises to validate backup integrity.

## Continuous Improvement

Security requirements feed back into `prompts/BUILD_SPEC.json` so automation agents enforce updated guardrails. As new services come online, extend the diagrams to document trust boundaries and update mitigation matrices accordingly.
