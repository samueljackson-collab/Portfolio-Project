# Architecture

Stack: Python, Jinja2, WeasyPrint, Celery workers.

Data/Control flow: Ingest data via API, render templates, generate PDFs, sign with GPG, and distribute via S3/email.

Dependencies:
- Python, Jinja2, WeasyPrint, Celery workers.
- Env/config: see README for required secrets and endpoints.
