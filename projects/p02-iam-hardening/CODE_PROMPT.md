# P02 — Code Prompt (Instructional Version)

**Goal:** Generate a detailed implementation plan and scaffolding for IAM Security Hardening without emitting any production code, secrets, or sample data.

## What to Request
- High-level module breakdown (e.g., policy authoring, validation tooling, deployment automation, observability hooks).
- Proposed file and directory structure for `src/`, `policies/`, `tests/`, and automation scripts.
- Configuration surfaces (environment variables, Make targets, CLI flags) with defaults and security notes.
- Acceptance criteria covering least-privilege requirements, policy validation coverage, and alerting behaviors.
- Validation and QA steps (linters, policy simulators, unit/integration/E2E test outlines, canary deployments).
- Rollback and safety guardrails for IAM changes.

## Output Expectations
- Provide instructions, checklists, and scaffolding only; **do not output code, JSON policies, or credentials**.
- Use bullet points, tables, and pseudo-file trees to illustrate structure.
- Defer actual code generation and data emission to downstream runs that will consume this plan.

## Example Response Outline
1. **Modules & Responsibilities** — Short table listing each module and its purpose.
2. **File Tree** — Pseudo-structure for source, policies, tests, and CI/CD configs.
3. **Configuration Matrix** — Environment variables/inputs with defaults and validation rules.
4. **Acceptance Criteria** — Verifiable, testable checks tied to IAM least-privilege goals.
5. **Validation Plan** — Tools, commands, and expected outcomes (no code output).
6. **Follow-up Prompts** — Specific next-step prompts to generate code, tests, and policies in later runs.
