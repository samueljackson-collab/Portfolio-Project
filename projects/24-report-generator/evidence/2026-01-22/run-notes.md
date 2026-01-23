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
