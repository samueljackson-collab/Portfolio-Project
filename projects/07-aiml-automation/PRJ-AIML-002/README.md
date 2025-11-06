# PRJ-AIML-002 — Document Packaging Automation

This folder contains the developer-facing scaffolding for the document packaging
pipeline. Runtime automation combines tabular datasets, reusable prompt
templates, and light-weight orchestration so engineers can stage document
bundles without copying the AI playbook into public documentation.

## Directory Layout
- `src/` – Python package implementing dataset adapters, prompt assembly, and
  orchestration helpers.
- `src/cli.py` – Minimal CLI wrapper used for smoke-testing the workflow
  locally. The real deployment swaps out the default runner with a model
  integration.

## Module Summary
- `adapters.py` – Parses CSV/TSV/JSON sources into dictionaries and exposes a
  `chunk_records` helper for batching large datasets.
- `prompt_builder.py` – Provides the `PromptTemplate` dataclass plus helper
  functions for rendering prompts using string substitution.
- `workflow.py` – Defines the `PackagingJob` orchestration primitive and a
  reference post-processor used by integration tests.
- `cli.py` – Offers a thin CLI around the core modules. It is safe to execute
  in local environments because the default model runner simply echoes the
  prompts back. Pass `--dry-run` to inspect prompts without invoking the
  runner.

## Getting Started
1. Install Python 3.11+.
2. Run `python projects/07-aiml-automation/PRJ-AIML-002/src/cli.py \
   sample.csv sample-template.txt` to exercise the workflow. Provide
   `--uppercase` to apply the reference post-processor or `--dry-run` to inspect
   prompts only.
3. Implementation plan, milestone breakdown, and prompt-engineering notes live
   under `docs/private/projects/07-aiml-automation/PRJ-AIML-002/`.

## Development Notes
- Add regression tests under `tests/prj_aiml_002/` when extending the pipeline.
- Keep sensitive model prompts, evaluation rubrics, and credential references in
  the private docs directory and environment-specific secret stores.
