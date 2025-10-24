# Documentation Contribution Guide

This guide supplements the root-level `CONTRIBUTING.md` by clarifying expectations for documentation and knowledge assets.

## Structure Principles
- Prefer task-based organization—each procedure gets its own heading.
- Use tables for command summaries and troubleshooting matrices.
- Cross-link heavily so that readers can navigate between ADRs, runbooks, and architecture content.

## Workflow
1. Identify the document to update and check for existing style notes.
2. Draft content in Markdown, using fenced code blocks for commands and Mermaid for diagrams.
3. Run `prettier --write` on documentation directories to maintain formatting.
4. Submit PRs with before/after screenshots when diagrams or UI references change.

## Templates
- Architecture Decision Records: `docs/templates/adr-template.md` (coming soon).
- Runbooks: `docs/templates/runbook-template.md` (coming soon).

## Review Checklist
- [ ] Links verified (use `markdown-link-check` before merging).
- [ ] Commands tested in a clean environment.
- [ ] Screenshots updated if UI changed.
- [ ] Metadata (last updated, version) refreshed where applicable.

