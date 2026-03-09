# README Governance Policy

## Purpose
This policy defines how README documentation is maintained across the portfolio repository so engineering, operations, and security stakeholders can trust that docs reflect the current system state.

## Required Update Cadence

| Documentation Type | Cadence | Trigger-Based Override |
| --- | --- | --- |
| Root and area README files | At least monthly (every 30 days) | Update in the same PR whenever architecture, setup, testing, risk, or roadmap changes |
| Project README files (`projects/`, `projects-new/`) | At least once per sprint (or every 14 days) | Update in the same PR for feature, infra, or operational behavior changes |
| Terraform README files (`terraform/`) | At least monthly and before each infra release | Update in the same PR for module/input/output/security control changes |

## Owner Roles per Project Area

| Area | Primary Documentation Owner | Secondary/Review Owner | Scope |
| --- | --- | --- | --- |
| `projects/` | Platform Portfolio Maintainer | QA & Reliability Lead | Legacy and canonical project guides/runbooks |
| `projects-new/` | Solutions Architecture Lead | Security Engineering Lead | Net-new project documentation and implementation guidance |
| `terraform/` | Infrastructure as Code Lead | Cloud Security Lead | Terraform usage, modules, state, and operational runbooks |
| `.github/` process docs and templates | Developer Experience Lead | Repository Maintainer | CI/doc governance workflows and contribution templates |

## Evidence-Link Expectations

Every README update that is required by this policy must include verifiable evidence links:

1. **Change evidence**: At least one link to architecture/design source (`ARCHITECTURE.md`, ADR, diagram, or equivalent).
2. **Validation evidence**: At least one link to testing/verification source (`TESTING.md`, CI run summary, or report).
3. **Risk evidence**: At least one link to risk/security source (`RISK_REGISTER.md`, threat model, security runbook, or issue).
4. **Roadmap evidence** (if roadmap changed): Link to the roadmap tracker, milestone, or backlog issue.

Use relative links whenever possible so evidence remains portable across forks.

## Compliance and Reporting

- PRs must complete the README governance checklist in `.github/pull_request_template.md`.
- Scheduled CI runs the README validator and markdown link checker.
- If non-compliance is found, CI auto-opens an issue containing the report artifact for triage.
