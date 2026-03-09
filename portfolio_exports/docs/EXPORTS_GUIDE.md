# Portfolio Exports — Documentation Guide

## Directory Map

- `github/` — README templates ready to customize per project.
- `diagrams/` — Mermaid diagrams for architecture quick looks.
- `runbooks/` — Operations runbooks aligned to the portfolio runbook structure.
- `wikijs/` — Wiki.js page templates for knowledge base ingestion.
- `docs/` — Cross-linking documentation and the master index.

## Naming Conventions

All export artifacts use a shared slug derived from the project name and follow these patterns:

- `github/<slug>_README.md`
- `diagrams/<slug>.mmd`
- `runbooks/<slug>_runbook.md`
- `wikijs/<slug>.md`

## How to Extend

1. Add the new project to `PORTFOLIO_SURVEY.md`.
2. Create new export artifacts using the naming patterns above.
3. Update `MASTER_INDEX.md` to include the new links.

## Cross-References

- Master index: `MASTER_INDEX.md`
- Portfolio survey: `../../PORTFOLIO_SURVEY.md`
- Runbook structure source: `../../PR_RUNBOOKS_DESCRIPTION.md`
