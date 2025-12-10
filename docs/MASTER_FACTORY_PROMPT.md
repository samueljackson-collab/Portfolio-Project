# Master Factory Prompt

## Purpose
This document defines the default behavior rules for any factory-style prompt execution within the portfolio. It clarifies what "done" means so downstream users request and deliver complete, runnable outputs rather than intermediary prompt snippets.

## Behavior Rules
- **Produce complete deliverables.** Responses must include everything required for a working solution: runnable code, configuration, supporting data samples, and user-facing documentation or instructions. Start assembling these artifacts in the very first response instead of deferring to “future work.”
- **Do not stop at prompt drafts.** If a user asks for a prompt, also supply the fully realized assets (code, data, docs) that the prompt would produce so the requester can execute immediately.
- **Assume execution-ready outputs.** Provide file names, directory structure, and any commands necessary to run or validate the generated solution.
- **Document dependencies.** Call out runtime requirements, environment variables, secrets, and install steps so the deliverable can be reproduced without guesswork.
- **Align with safety and compliance.** Preserve security, privacy, and licensing considerations in all generated assets, noting any constraints or required approvals.

## Code Generation Expectations
- Default to **generating full, runnable code** (not pseudocode) that compiles or executes as written, including entry points, configuration, and test coverage when applicable.
- When templates or placeholders are unavoidable, mark them explicitly and explain how to replace them so the final output remains runnable.
- Prefer **concrete examples and sample data** that exercise the code paths and demonstrate expected behavior.
- Include concise **run instructions** (e.g., commands, scripts, or API calls) and, when appropriate, minimal tests to validate correctness.
- Structure the response so files can be copied directly into a repository with minimal manual stitching.
- Proactively surface **next actions** (e.g., “seed the database with sample_rows.csv before running `npm start`”) so downstream owners can continue execution without new prompts.

## Deliverable Startup Recipe
- Begin each engagement by proposing a minimal, runnable scaffold. Include:
  - A directory map (e.g., `src/`, `tests/`, `config/`, `docs/`).
  - Named entry points (scripts, services, or notebooks) with brief role descriptions.
  - At least one sample data file or inline fixture that demonstrates expected input/output.
  - A short README snippet that explains setup and a single “happy path” run command.
- If the request is broad, ship a **first working slice** (e.g., one endpoint, one pipeline stage, or one UI route) so users can execute something immediately while you elaborate further.

## Deliverable Checklist for Downstream Users
- [ ] Source code with clear entry points and comments where necessary.
- [ ] Configuration files, environment variable references, and secret management guidance.
- [ ] Sample or synthetic data sufficient to run the solution end-to-end.
- [ ] Documentation explaining setup, execution, and verification steps.
- [ ] Notes on performance, security, and compliance considerations specific to the deliverable.

Following these rules ensures factory prompts yield production-ready assets, reducing rework and ambiguity for downstream teams.
