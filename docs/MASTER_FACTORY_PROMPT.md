# MASTER_FACTORY_PROMPT Ruleset

Use this ruleset whenever generating portfolio deliverables with the "Master Factory" flow. Each project run must emit a unified markdown artifact that contains 12 clearly labelled sections:

1. README / Overview
2. Architecture & IaC Diagrams (Mermaid + ASCII; include CI/CD and IaC perspectives)
3. CI/CD Blueprint
4. Code Prompts & Generation Guardrails
5. Testing Suite
6. Operations & Runbooks
7. Reporting & Analytics
8. Observability
9. Security & Compliance
10. Risk Management
11. Architecture Decision Records (ADRs)
12. Business Narrative & Outcomes

Additional standards:
- Diagrams must be valid Mermaid plus ASCII sketches—no placeholders. Reflect how CI/CD interacts with IaC and runtime services.
- Content should reference the project scope, tech stack, and measurable outcomes; avoid filler text.
- Outputs live inside the target project folder under a `master-factory/` subdirectory as `MASTER_FACTORY.md`.
- CI/CD and IaC strategies must align with the project’s existing stack and name.
- Include prompts for developers, reviewers, and IaC authors to keep AI-generated code consistent with repo practices.

Validate that every generated artifact follows these bullets before submission.
