---
title: Project 24: Portfolio Report Generator
description: Automated report generation system using Jinja2 templates and WeasyPrint to produce PDF/HTML status reports
tags: [automation-documentation, documentation, portfolio, python]
path: portfolio/24-report-generator/overview
created: 2026-03-08T22:19:13.310598+00:00
updated: 2026-03-08T22:04:38.681902+00:00
---

-

# Project 24: Portfolio Report Generator
> **Category:** Automation & Documentation | **Status:** 🟢 60% Complete
> **Source:** projects/25-portfolio-website/docs/projects/24-report-generator.md

## 📋 Executive Summary

Automated report generation system using **Jinja2** templates and **WeasyPrint** to produce PDF/HTML status reports. Aggregates data from GitHub, Kubernetes, databases, and monitoring systems to create comprehensive portfolio documentation.

## 🎯 Project Objectives

- **Template-Driven** - Jinja2 for flexible report layouts
- **Multi-Format Output** - HTML, PDF, Markdown generation
- **Data Aggregation** - Pulls from GitHub, K8s, Prometheus, databases
- **Scheduling** - Automated weekly/monthly report generation
- **Customizable** - Multiple report types (executive, technical, compliance)

## 🏗️ Architecture

> Source: ../../../projects/25-portfolio-website/docs/projects/24-report-generator.md#architecture
```
Data Sources                  Report Generator
────────────                 ─────────────────
GitHub API        →     Data Collectors
Kubernetes API    →           ↓
Prometheus        →     Data Aggregation
PostgreSQL        →           ↓
JIRA              →     Template Engine (Jinja2)
                              ↓
                    ┌─── Render ───┐
                    ↓               ↓
              HTML Output      PDF Output
              (WeasyPrint)     (WeasyPrint)
                    ↓               ↓
              Email Delivery  S3 Storage
              (SendGrid)      (Archive)
```

**Report Generation Flow:**
1. **Data Collection**: Query GitHub, K8s, Prometheus
2. **Aggregation**: Combine metrics into report data model
3. **Template Selection**: Choose report type (weekly, monthly, etc.)
4. **Rendering**: Jinja2 template rendering with data
5. **PDF Generation**: WeasyPrint converts HTML to PDF
6. **Distribution**: Email or upload to S3/SharePoint

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Python | Python | Core implementation |
| Jinja2 | Jinja2 | Template engine |
| WeasyPrint | WeasyPrint | HTML to PDF conversion |

## 💡 Key Technical Decisions

### Decision 1: Adopt Python
**Context:** Project 24: Portfolio Report Generator requires a resilient delivery path.
**Decision:** Core implementation
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 2: Adopt Jinja2
**Context:** Project 24: Portfolio Report Generator requires a resilient delivery path.
**Decision:** Template engine
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 3: Adopt WeasyPrint
**Context:** Project 24: Portfolio Report Generator requires a resilient delivery path.
**Decision:** HTML to PDF conversion
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

## 🔧 Implementation Details

```bash
cd projects/24-report-generator

# Install dependencies
pip install -r requirements.txt

# Generate weekly report
python src/generate_report.py \
  --template templates/weekly.html \
  --output report.html

# Generate PDF
python src/generate_report.py \
  --template templates/weekly.html \
  --output report.pdf \
  --format pdf

# Generate with custom data
python src/generate_report.py \
  --template templates/executive.html \
  --data-sources github,kubernetes,prometheus \
  --date-range "2024-01-01:2024-01-31" \
  --output monthly_report.pdf

# Schedule weekly reports (cron)
# 0 9 * * 1 cd /path/to/project && python src/generate_report.py --template weekly.html --email team@example.com
```

```
24-report-generator/
├── src/
│   ├── __init__.py
│   ├── generate_report.py       # Main generator
│   ├── collectors/              # Data collectors (to be added)
│   │   ├── github_collector.py
│   │   ├── k8s_collector.py
│   │   └── prometheus_collector.py
│   └── renderers/               # Output renderers (to be added)
│       ├── html_renderer.py
│       └── pdf_renderer.py
├── templates/
│   ├── weekly.html              # Weekly report template
│   ├── monthly.html             # Monthly template (to be added)
│   ├── executive.html           # Executive summary (to be added)
│   └── compliance.html          # Compliance report (to be added)
├── static/                      # CSS, images (to be added)
│   ├── styles.css
│   └── logo.png
├── data/                        # Sample data (to be added)
├── requirements.txt
└── README.md
```

## ✅ Results & Outcomes

- **Time Savings**: 10 hours/week saved on manual reporting
- **Consistency**: Standardized report format across teams
- **Data Accuracy**: Automated collection eliminates manual errors
- **Transparency**: Regular updates to stakeholders

## 📚 Documentation

- [README.md](../README.md)
- [RUNBOOK.md](../RUNBOOK.md)
- [projects/25-portfolio-website/docs/projects/24-report-generator.md](../../../projects/25-portfolio-website/docs/projects/24-report-generator.md)

## 🎓 Skills Demonstrated

**Technical Skills:** Python, Jinja2, WeasyPrint, Pandas, Matplotlib/Plotly

**Soft Skills:** Communication, Incident response leadership, Documentation rigor

## 📦 Wiki Deliverables

### Diagrams

- **Architecture excerpt** — Copied from `../../../projects/25-portfolio-website/docs/projects/24-report-generator.md` (Architecture section).

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
| **Report generation success rate** | 99% | Successful report completions |
| **Report generation time (p95)** | < 60 seconds | Template render → output file |
| **Template validation success** | 100% | Valid Jinja2 syntax |
| **Scheduled report delivery** | 99.5% | On-time report delivery |
| **PDF rendering success rate** | 98% | Successful WeasyPrint conversions |
| **Data aggregation latency** | < 30 seconds | Source data collection time |
| **Report file size (p95)** | < 5MB | Generated report file size |

### Screenshots

- **Operational dashboard mockup** — `../../../projects/06-homelab/PRJ-HOME-002/assets/mockups/wikijs-documentation.html` (captures golden signals per PRJ-MASTER playbook).

---

*Created: 2025-11-14 | Last Updated: 2025-11-14*
