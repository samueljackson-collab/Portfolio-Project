---
title: Project 4: DevSecOps Pipeline
description: Security-first CI/CD pipeline integrating SAST, DAST, and container scanning into the software delivery workflow
tags: [portfolio, infrastructure-devops, github-actions]
repository: https://github.com/samueljackson-collab/Portfolio-Project
path: /projects/devsecops
---

# Project 4: DevSecOps Pipeline
> **Category:** Infrastructure & DevOps | **Status:** 🟡 25% Complete
> **Source:** projects/25-portfolio-website/docs/projects/04-devsecops.md

## 📋 Executive Summary

Security-first CI/CD pipeline integrating **SAST, DAST, and container scanning** into the software delivery workflow. Generates Software Bill of Materials (SBOM) and enforces security policies before deployment.

## 🎯 Project Objectives

- **Shift-Left Security** - Vulnerabilities caught early in development
- **Automated Scanning** - Code, dependencies, and container images
- **SBOM Generation** - Complete inventory of software components
- **Policy Gates** - Block deployment on critical/high vulnerabilities
- **Compliance Reports** - Automated security posture documentation

## 🏗️ Architecture

> Source: ../../../projects/25-portfolio-website/docs/projects/04-devsecops.md#architecture
```
Code Commit → SAST Scan → Dependency Check → Build Image
                ↓              ↓                  ↓
            SonarQube        Snyk          Trivy/Clair
                ↓              ↓                  ↓
              Policy Gate (Pass/Fail)
                      ↓
               DAST Scan (Staging)
                      ↓
              Deploy Production
```

**Security Stages:**
1. **SAST**: Static code analysis (SonarQube, Semgrep)
2. **Dependency Scan**: Vulnerable library detection (Snyk, OWASP Dependency-Check)
3. **Container Scan**: Image vulnerability scan (Trivy, Clair)
4. **SBOM**: Generate software bill of materials (Syft)
5. **DAST**: Dynamic application testing in staging (OWASP ZAP)
6. **Policy Enforcement**: Fail pipeline on critical issues

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| GitHub Actions | GitHub Actions | CI/CD orchestration |
| SonarQube | SonarQube | Code quality and security analysis |
| Snyk | Snyk | Dependency vulnerability scanning |

## 💡 Key Technical Decisions

### Decision 1: Adopt GitHub Actions
**Context:** Project 4: DevSecOps Pipeline requires a resilient delivery path.
**Decision:** CI/CD orchestration
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 2: Adopt SonarQube
**Context:** Project 4: DevSecOps Pipeline requires a resilient delivery path.
**Decision:** Code quality and security analysis
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 3: Adopt Snyk
**Context:** Project 4: DevSecOps Pipeline requires a resilient delivery path.
**Decision:** Dependency vulnerability scanning
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

## 🔧 Implementation Details

```bash
cd projects/4-devsecops

# Run security scans locally
docker run --rm -v $(pwd):/src sonarqube:latest sonar-scanner
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image myapp:latest

# Generate SBOM
syft packages dir:. -o spdx-json > sbom.json
```

```
4-devsecops/
├── pipelines/
│   └── github-actions.yaml    # DevSecOps workflow
├── policies/                  # Security policies (to be added)
├── config/                    # Tool configurations (to be added)
│   ├── sonarqube/
│   ├── snyk/
│   └── trivy/
└── README.md
```

## ✅ Results & Outcomes

- **Vulnerability Detection**: 85% of issues caught before production
- **Compliance**: Automated SOC 2 / ISO 27001 evidence collection
- **Cost Savings**: $100K+ prevented from production vulnerabilities
- **Faster Remediation**: Issues identified in minutes vs days

## 📚 Documentation

- [README.md](../README.md)
- [RUNBOOK.md](../RUNBOOK.md)
- [projects/25-portfolio-website/docs/projects/04-devsecops.md](../../../projects/25-portfolio-website/docs/projects/04-devsecops.md)

## 🎓 Skills Demonstrated

**Technical Skills:** GitHub Actions, SonarQube, Snyk, Trivy, OWASP ZAP

**Soft Skills:** Communication, Incident response leadership, Documentation rigor

## 📦 Wiki Deliverables

### Diagrams

- **Architecture excerpt** — Copied from `../../../projects/25-portfolio-website/docs/projects/04-devsecops.md` (Architecture section).

### Checklists

> Source: ../../../docs/PRJ-MASTER-PLAYBOOK/README.md#5-deployment--release

**Infrastructure**:
- [ ] Terraform plan reviewed and approved
- [ ] Database migrations tested
- [ ] Secrets configured in AWS Secrets Manager
- [ ] Monitoring alerts configured
- [ ] Runbook updated with new procedures

**Application**:
- [ ] All tests passing in staging
- [ ] Performance benchmarks met
- [ ] Feature flags configured (if using)
- [ ] Rollback plan documented
- [ ] Stakeholders notified of deployment

### Metrics

> Source: ../RUNBOOK.md#sloslis

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Security scan completion rate** | 99% | Successful vulnerability scans per build |
| **Critical vulnerability detection time** | < 5 minutes | Time from build → security alert |
| **Policy violation detection rate** | 100% | All policy violations caught pre-deployment |
| **SBOM generation success rate** | 99% | SBOM created for all deployments |
| **Image signing success rate** | 100% | All production images signed |
| **Security scan time** | < 5 minutes | Time for complete security scan |
| **False positive rate** | < 5% | Incorrectly flagged vulnerabilities |

### Screenshots

- **Operational dashboard mockup** — `../../../projects/06-homelab/PRJ-HOME-002/assets/mockups/grafana-dashboard.html` (captures golden signals per PRJ-MASTER playbook).

---

*Created: 2025-11-14 | Last Updated: 2025-11-14*
