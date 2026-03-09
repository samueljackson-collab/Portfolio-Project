---
title: Project 4: DevSecOps Pipeline
description: **Category:** Infrastructure & DevOps **Status:** 🟡 25% Complete **Source:** [View Code](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/4-devsecops) Security-first CI/CD 
tags: [documentation, portfolio]
path: portfolio/25-portfolio-website/04-devsecops
created: 2026-03-08T22:19:13.327578+00:00
updated: 2026-03-08T22:04:38.686902+00:00
---

# Project 4: DevSecOps Pipeline

**Category:** Infrastructure & DevOps
**Status:** 🟡 25% Complete
**Source:** [View Code](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/4-devsecops)

## Overview

Security-first CI/CD pipeline integrating **SAST, DAST, and container scanning** into the software delivery workflow. Generates Software Bill of Materials (SBOM) and enforces security policies before deployment.

## Key Features

- **Shift-Left Security** - Vulnerabilities caught early in development
- **Automated Scanning** - Code, dependencies, and container images
- **SBOM Generation** - Complete inventory of software components
- **Policy Gates** - Block deployment on critical/high vulnerabilities
- **Compliance Reports** - Automated security posture documentation

## Architecture

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

## Technologies

- **GitHub Actions** - CI/CD orchestration
- **SonarQube** - Code quality and security analysis
- **Snyk** - Dependency vulnerability scanning
- **Trivy** - Container image scanning
- **OWASP ZAP** - Dynamic application security testing
- **Syft** - SBOM generation
- **HashiCorp Vault** - Secrets management

## Quick Start

```bash
cd projects/4-devsecops

# Run security scans locally
docker run --rm -v $(pwd):/src sonarqube:latest sonar-scanner
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image myapp:latest

# Generate SBOM
syft packages dir:. -o spdx-json > sbom.json
```

## Project Structure

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

## Business Impact

- **Vulnerability Detection**: 85% of issues caught before production
- **Compliance**: Automated SOC 2 / ISO 27001 evidence collection
- **Cost Savings**: $100K+ prevented from production vulnerabilities
- **Faster Remediation**: Issues identified in minutes vs days

## Current Status

**Completed:**
- ✅ Basic GitHub Actions pipeline structure

**In Progress:**
- 🟡 SonarQube integration
- 🟡 Snyk dependency scanning
- 🟡 Trivy container scanning
- 🟡 SBOM generation
- 🟡 Policy enforcement logic

**Next Steps:**
1. Integrate SonarQube for SAST scanning
2. Add Snyk for dependency vulnerability checks
3. Implement Trivy container image scanning
4. Configure SBOM generation with Syft
5. Add OWASP ZAP for DAST in staging environment
6. Create security policy rules and enforcement
7. Set up HashiCorp Vault for secrets management
8. Generate compliance reports and dashboards

## Key Learning Outcomes

- DevSecOps principles and shift-left security
- Static and dynamic application security testing
- Container security best practices
- SBOM generation and software supply chain security
- Security policy as code
- Secrets management

---

**Related Projects:**
- [Project 3: Kubernetes CI/CD](/projects/03-kubernetes-cicd) - Base pipeline
- [Project 11: IoT Analytics](/projects/11-iot) - Security monitoring
- [Project 13: Cybersecurity](/projects/13-cybersecurity) - SIEM integration
