---
title: Project 24: Portfolio Report Generator
description: **Category:** Automation & Documentation **Status:** 🟢 60% Complete **Source:** [View Code](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/24-report-generator) Automated 
tags: [documentation, portfolio]
path: portfolio/25-portfolio-website/24-report-generator
created: 2026-03-08T22:19:13.329866+00:00
updated: 2026-03-08T22:04:38.693902+00:00
---

# Project 24: Portfolio Report Generator

**Category:** Automation & Documentation
**Status:** 🟢 60% Complete
**Source:** [View Code](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/24-report-generator)

## Overview

Automated report generation system using **Jinja2** templates and **WeasyPrint** to produce PDF/HTML status reports. Aggregates data from GitHub, Kubernetes, databases, and monitoring systems to create comprehensive portfolio documentation.

## Key Features

- **Template-Driven** - Jinja2 for flexible report layouts
- **Multi-Format Output** - HTML, PDF, Markdown generation
- **Data Aggregation** - Pulls from GitHub, K8s, Prometheus, databases
- **Scheduling** - Automated weekly/monthly report generation
- **Customizable** - Multiple report types (executive, technical, compliance)

## Architecture

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

## Technologies

- **Python** - Core implementation
- **Jinja2** - Template engine
- **WeasyPrint** - HTML to PDF conversion
- **Pandas** - Data manipulation and analysis
- **Matplotlib/Plotly** - Chart generation
- **PyGithub** - GitHub API integration
- **kubernetes-client** - K8s API access
- **prometheus-api-client** - Metrics queries

## Quick Start

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

## Project Structure

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

## Business Impact

- **Time Savings**: 10 hours/week saved on manual reporting
- **Consistency**: Standardized report format across teams
- **Data Accuracy**: Automated collection eliminates manual errors
- **Transparency**: Regular updates to stakeholders
- **Compliance**: Automated SOC 2 / ISO 27001 evidence collection

## Current Status

**Completed:**
- ✅ Core report generator with Jinja2
- ✅ Weekly HTML template
- ✅ Basic PDF generation with WeasyPrint
- ✅ Command-line interface

**In Progress:**
- 🟡 Data collector implementations
- 🟡 Additional report templates
- 🟡 Scheduling integration
- 🟡 Email delivery

**Next Steps:**
1. Implement GitHub API collector (commits, PRs, issues)
2. Add Kubernetes collector (deployments, resource usage)
3. Build Prometheus collector (SLO metrics, uptime)
4. Create monthly and executive report templates
5. Add chart generation with Matplotlib/Plotly
6. Implement email delivery with SendGrid
7. Add S3 upload for report archival
8. Create scheduling with cron or Airflow
9. Build web UI for report customization
10. Add report versioning and change tracking

## Key Learning Outcomes

- Report automation techniques
- Template engine design (Jinja2)
- PDF generation from HTML
- API integration patterns
- Data aggregation and analysis
- Document styling with CSS
- Scheduling and cron jobs

---

**Related Projects:**
- [Project 23: Monitoring](/projects/23-monitoring) - Metrics data source
- [Project 25: Portfolio Website](/projects/25-portfolio-website) - Documentation hub
- [Project 6: MLOps](/projects/06-mlops) - Model performance reports
