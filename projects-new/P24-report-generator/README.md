# P24 – Automated Report Generator

Generates PDF/HTML reports from templated data feeds with signed delivery.

## Quick start
- Stack: Python, Jinja2, WeasyPrint, Celery workers.
- Flow: Ingest data via API, render templates, generate PDFs, sign with GPG, and distribute via S3/email.
- Run: make lint then pytest tests
- Operate: Rotate signing keys, monitor Celery queue depth, and cache assets for performance.
