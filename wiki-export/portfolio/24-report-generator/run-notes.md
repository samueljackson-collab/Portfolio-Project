---
title: Report Generation Evidence (2026-01-22)
description: - Command: `pip install -r requirements.txt` - Command: `python src/generate_report.py generate-all --output-dir /workspace/Portfolio-Project/projects/24-report-generator/evidence/2026-01-22/reports` 
tags: [documentation, portfolio]
path: portfolio/24-report-generator/run-notes
created: 2026-03-08T22:19:13.316952+00:00
updated: 2026-03-08T22:04:38.668902+00:00
---

# Report Generation Evidence (2026-01-22)

## Inputs
- Command: `pip install -r requirements.txt`
- Command: `python src/generate_report.py generate-all --output-dir /workspace/Portfolio-Project/projects/24-report-generator/evidence/2026-01-22/reports`
- Command: `python (timed generation script with ReportGenerator)`
- Data sources: Portfolio root `/workspace/Portfolio-Project` scanned via `PortfolioDataCollector`

## Outputs
- Dependency install log: `pip-install.log`
- Report generation log: `generate-all.log`
- Generated reports: `reports/` (HTML)
- Timed reports: `timed-reports/` (HTML)
- Timing data: `report-timings.csv`

## Notes
- PDF generation used the built-in fallback renderer because WeasyPrint was unavailable in the environment.
