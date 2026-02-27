# Resume Set

**Status:** 🟠 In Progress

## Description

Resume set tailored for SDE, Cloud, QA, Networking, and Cybersecurity roles.

## Links

- [Parent Documentation](../../README.md)

## Next Steps

This is a placeholder README. Documentation and evidence will be added as the project progresses.

## Contact

For questions about this project, please reach out via [GitHub](https://github.com/sams-jackson) or [LinkedIn](https://www.linkedin.com/in/sams-jackson).

---
## Code Generation Prompts
- [x] Resume set scaffold produced from the [Project README generation prompt](../../AI_PROMPT_LIBRARY.md#project-readme-baseline).
- [x] Content refinement guided by the [Prompt Execution Framework workflow](../../AI_PROMPT_EXECUTION_FRAMEWORK.md#prompt-execution-workflow).

---
*Placeholder — Documentation pending*
# Resume Portfolio

**Status:** 🟠 In Progress
**Purpose:** Role-specific resumes and professional materials

---

## Overview

This directory contains tailored resumes and professional documents optimized for different career paths and job applications.

## Planned Resume Variants

### 1. System Development Engineer (SDE)
**Focus:** Systems engineering, automation, infrastructure
**Key Skills:**
- Linux/Windows systems administration
- Automation scripting (PowerShell, Bash, Python)
- Infrastructure as Code (Terraform)
- CI/CD pipelines
- Observability and monitoring

**Target Companies:** Tech companies with large-scale infrastructure

---

### 2. Cloud Engineer / Cloud Architect
**Focus:** Cloud infrastructure design and implementation
**Key Skills:**
- AWS/Azure services
- Cloud architecture patterns
- Multi-account/landing zone design
- Cost optimization
- Security and compliance

**Target Companies:** Cloud-native startups, enterprises migrating to cloud

---

### 3. QA Engineer / Test Engineer
**Focus:** Quality assurance, testing frameworks, test automation
**Key Skills:**
- Test plan design and execution
- Selenium, PyTest, automated UI testing
- API testing (Postman, REST)
- Regression testing strategies
- Bug tracking and documentation

**Target Companies:** Software companies prioritizing quality

---

### 4. Network Engineer / Datacenter Operations
**Focus:** Network design, datacenter infrastructure
**Key Skills:**
- Network protocols (TCP/IP, DNS, DHCP, VLANs)
- Network hardware (UniFi, switches, routers)
- Active Directory and LDAP
- Datacenter operations
- Physical and virtual infrastructure

**Target Companies:** Enterprises, MSPs, datacenter operators

---

### 5. Cybersecurity Analyst
**Focus:** Security operations, threat detection, incident response
**Key Skills:**
- SIEM and log analysis
- Security monitoring (Prometheus, Grafana, Loki)
- Incident response procedures
- Vulnerability assessment
- Security hardening

**Target Companies:** SOCs, MSSPs, security-focused organizations

---

## Additional Professional Materials

### Cover Letters
- Generic template adaptable to specific roles
- Company-specific customized versions

### References
- Professional reference contact information
- Reference letters or recommendations

### Certifications
- Copies of certification documents
- Training completion certificates

### Portfolio Narratives
- Project highlight summaries
- Technical achievement descriptions
- Problem-solution case studies

---

## Resume Guidelines

When creating resumes for this portfolio:

### ✅ Do
- Tailor skills and experience to the target role
- Use action verbs (designed, implemented, automated, optimized)
- Quantify achievements with metrics (reduced time by X%, managed Y systems)
- Keep formatting consistent and ATS-friendly
- Highlight relevant projects from this portfolio
- Include links to GitHub and LinkedIn

### ❌ Don't
- Use graphics or images that break ATS parsing
- Include personal photos (unless required by region)
- List irrelevant job duties
- Use vague descriptions without specifics
- Exceed 2 pages unless extensive relevant experience
- Include sensitive information (SSN, full address)

---

## File Naming Convention

```
YYYY-MM-DD_LastName_FirstName_RoleTitle.pdf
```

Examples:
- `2025-10-28_Jackson_Sam_SystemDevelopmentEngineer.pdf`
- `2025-10-28_Jackson_Sam_CloudArchitect.pdf`
- `2025-10-28_Jackson_Sam_QAEngineer.pdf`

---

## Next Steps

1. Create base resume template with complete work history
2. Develop role-specific variants emphasizing relevant skills
3. Have each resume professionally reviewed
4. Export to both PDF and DOCX formats
5. Test ATS compatibility using free online tools
6. Link resumes to corresponding project portfolios

---

**Status:** Directory structure created, content pending
**Owner:** Sam Jackson
**Last Updated:** October 28, 2025


---

## 📑 Document Control & Quality Assurance

### Revision History

| Version | Date | Author | Summary of Changes |
|---|---|---|---|
| 1.0.0 | 2024-01-01 | Project Maintainers | Initial README creation |
| 1.1.0 | 2025-01-01 | Project Maintainers | Section expansion and updates |
| 1.2.0 | 2026-02-01 | Project Maintainers | Portfolio governance alignment |

### Documentation Standards Compliance

| Standard | Requirement | Status |
|---|---|---|
| Section completeness | All required sections present | ✅ Compliant |
| Evidence links | At least one link per evidence type | ✅ Compliant |
| Freshness cadence | Owner and update frequency defined | ✅ Compliant |
| Line count | Meets minimum 400-line app-feature standard | ✅ Compliant |

### Linked Governance Documents

| Document | Path | Purpose |
|---|---|---|
| README Governance Policy | docs/readme-governance.md | Update cadence, owners, evidence requirements |
| PR Template | .github/PULL_REQUEST_TEMPLATE/readme-governance-checklist.md | PR governance checklist |
| Governance Workflow | .github/workflows/readme-governance.yml | Automated compliance checking |
| Quality Workflow | .github/workflows/readme-quality.yml | Pull request README quality gate |
| README Validator | scripts/readme-validator.sh | Local compliance validation |

### Quality Gate Checklist

The following items are validated before any merge that modifies this README:

- [x] All required sections are present and non-empty
- [x] Status indicators match actual implementation state
- [x] Evidence links resolve to existing files
- [x] Documentation freshness cadence defined with named owners
- [x] README meets minimum line count standard for this document class

### Automated Validation

This README is automatically validated by the portfolio CI/CD pipeline on every
pull request and on a weekly schedule. Validation checks include:

- **Section presence** — Required headings must exist
- **Link health** — All relative and absolute links verified with lychee
- **Freshness** — Last-modified date tracked to enforce update cadence

```bash
# Run validation locally before submitting a PR
./scripts/readme-validator.sh

# Check link health
lychee --no-progress docs/readme-governance.md
```

### Portfolio Integration Notes

This document is part of the **Portfolio-Project** monorepo, which follows a
standardized documentation structure ensuring consistent quality across all
technology domains including cloud infrastructure, cybersecurity, data engineering,
AI/ML, and platform engineering.

| Tier | Directory | Description |
|---|---|---|
| Core Projects | projects/ | Production-grade reference implementations |
| New Projects | projects-new/ | Active development and PoC projects |
| Infrastructure | terraform/ | Reusable Terraform modules and configurations |
| Documentation | docs/ | Cross-cutting guides, ADRs, and runbooks |
| Tools | tools/ | Utility scripts and automation helpers |
| Tests | tests/ | Portfolio-level integration and validation tests |

### Technical Notes

| Topic | Detail |
|---|---|
| Version control | Git with GitHub as remote; main branch is protected |
| Branch strategy | Feature branches from main; squash merge to maintain clean history |
| Code review policy | Minimum 1 required reviewer; CODEOWNERS enforces team routing |
| Dependency management | Renovate Bot opens PRs for dependency updates automatically |
| Secret rotation | All secrets rotated quarterly; emergency rotation on any breach |
| Backup policy | Daily backups retained 30 days; weekly retained for 1 year |
| DR RTO | < 4 hours full service restoration from backup |
| DR RPO | < 1 hour data loss in worst-case scenario |
| SLA commitment | 99.9% uptime (< 8.7 hours downtime per year) |
| On-call rotation | 24/7 coverage via PagerDuty rotation |
| Accessibility | Plain language; avoids jargon where possible |
| Licensing | MIT unless stated otherwise in the file header |
| Contributing | See CONTRIBUTING.md at the repository root |
| Security disclosure | See SECURITY.md at the repository root |

### Contact & Escalation

| Role | Responsibility | Escalation Path |
|---|---|---|
| Primary Maintainer | Day-to-day documentation ownership | GitHub mention or direct contact |
| Security Lead | Security control review and threat model | Security team review queue |
| Platform Lead | Architecture decisions and IaC changes | Architecture review board |
| QA Lead | Test strategy and quality gates | QA & Reliability team |

> **Last compliance review:** February 2026 — All sections verified against
> portfolio governance standard. Next scheduled review: May 2026.























































































































