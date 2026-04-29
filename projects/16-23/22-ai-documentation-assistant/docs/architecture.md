# Architecture

## Overview
Pipeline ingests repositories and tickets, passes content through LLM services with guardrails, and opens change requests for human review.

## Component Breakdown
- **Ingestion Connectors:** Pull code diffs, commit messages, and ticket updates.
- **LLM Orchestrator:** Applies prompts, context windows, and policy filters for doc generation.
- **Review Console:** Allows SMEs to approve edits, leave feedback, and publish updates.
- **Documentation Portal:** Publishes final docs with freshness metadata and search.

## Diagrams & Flows
```text
Code/Tickets -> Ingestion -> LLM Orchestrator -> Draft Docs -> Review Console -> Documentation Portal
            Guardrails Service monitors PII/redaction across pipeline.
```
