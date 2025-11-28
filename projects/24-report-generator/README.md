# Project 24: Portfolio Report Generator

## Overview
Generates PDF/HTML status reports for the portfolio using Jinja2 templates and WeasyPrint.

## Architecture
- **Context:** Portfolio metrics and project status data are combined with branded templates to generate PDF/HTML reports that can be scheduled and distributed.
- **Decision:** Use a CLI/scheduler to gather metrics, render reports with Jinja2 and WeasyPrint, validate content, then push artifacts to object storage for email/chat distribution and archival.
- **Consequences:** Produces consistent, versioned reports with automation hooks, but depends on template governance to avoid broken layouts or stale branding.

[Mermaid source](assets/diagrams/architecture.mmd) · Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

## Run
```bash
pip install -r requirements.txt
python src/generate_report.py --template templates/weekly.html --output report.html
```
