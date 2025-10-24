# Implementation Plan — PRJ-AIML-002: Document Packaging Automation

> Internal use only. This plan was migrated from the project README to keep AI workflow guidance and prompt engineering notes in a restricted location.

## 1. Objectives
- Automate generation of packaged deliverables (Docs, PDFs, XLSX) from structured prompts and datasets.
- Provide a repeatable CLI entry point for engineers to run targeted packaging jobs or scheduled batches.
- Capture intermediate artefacts (prompt inputs, raw model responses, validation logs) for auditability.

## 2. System Outline
- **Source adapters** read project briefs, tabular data, and template fragments from Git, SharePoint exports, or local folders.
- **Prompt builder** composes LLM-ready instructions using YAML/JSON templates plus inline substitution of dataset values.
- **Generation engine** fans out prompts across selected models (OpenAI-compatible HTTP APIs or local inference endpoints).
- **Post-processing** normalises Markdown/HTML, merges tables, and produces final Docx/PDF/XLSX bundles.
- **Orchestrator** (Prefect or lightweight asyncio runner) coordinates adapters → prompt builder → generation → export, persisting run metadata in SQLite.

## 3. Milestones & Tasks

### Milestone A — Data & Template Layer (Week 1)
1. Finalise repository layout (`src/` package, `config/` for adapter settings, `templates/` for prompt scaffolds).
2. Build file-system adapter with schema validation and support for CSV/Excel ingestion.
3. Define template syntax (`${placeholder}`) and implement loader with Jinja2 environment + safety filters.
4. Unit tests for adapter edge cases (missing columns, invalid encodings, template parse errors).

### Milestone B — Prompt Engineering Layer (Week 2)
1. Create prompt catalogue YAML describing task, tone, output schema, retry policy.
2. Implement prompt assembly service that injects dataset rows, chunking large tables, and appends guardrails.
3. Provide dry-run mode that renders prompts without dispatching to models.
4. Add snapshot logging for assembled prompts and evaluation rubric used per job.

### Milestone C — Generation & QA (Week 3)
1. Integrate OpenAI-compatible client with retry, exponential backoff, and rate-limit tracking.
2. Normalize responses (Markdown to HTML) and enforce schema via Pydantic models.
3. Implement QA hooks: structural validation, grammar/lint checks, and diffing vs previous outputs.
4. Persist validated payloads and metadata, including prompt hashes and model IDs.

### Milestone D — Packaging & Distribution (Week 4)
1. Produce multi-format exports (Docx via python-docx, PDF via wkhtmltopdf container, XLSX via openpyxl).
2. Bundle outputs with manifest.json summarizing source data, prompts used, and QA verdicts.
3. Ship CLI commands: `package run <job>`, `package validate <job>`, and `package report <job>`.
4. Document hand-off checklist (permissions review, delivery log update, archival to S3 bucket).

## 4. Testing Strategy
- Pytest suites for adapters, prompt builder, generation workflow, and CLI commands.
- Golden-sample fixtures stored under `tests/fixtures/` for regression comparisons.
- CI pipeline steps: lint (`ruff`), type-check (`mypy`), unit tests, and optional nightly integration test hitting sandbox LLM endpoint.

## 5. Operations & Access Controls
- Secrets (API keys, SharePoint tokens) sourced from `.env` or Azure Key Vault; never committed.
- `docs/private/**` flagged with `export-ignore` in `.gitattributes` to keep internal docs out of packaged releases.
- Run metadata stored in local SQLite during development; promote to PostgreSQL instance for staging/production.

## 6. Open Questions & Follow-Ups
- Evaluate whether to standardise on Prefect or custom asyncio orchestrator for long-running jobs.
- Confirm licensing for wkhtmltopdf container usage in client environments.
- Determine retention policy for generated artefacts and decide between S3 lifecycle rules or manual cleanup CLI.
