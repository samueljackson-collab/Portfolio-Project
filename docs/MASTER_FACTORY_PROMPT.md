# Portfolio Project Generation Factory

This meta-prompt packages the instructions needed to generate the complete deliverable set for any of the P01–P25 portfolio projects. Use it when you want an AI to produce README drafts, architecture diagrams, testing plans, code prompts, runbooks, ADRs, threat models, and risk registers in one pass.

## How to Use

1. Copy the **Activation Prompt** below into your AI tool of choice.
2. Replace `PXX` with the project code and `<project name>` with the short title.
3. Run the prompt and wait for the AI to output the full deliverable pack in the prescribed order.
4. Review for accuracy, then file or commit the outputs into the matching project folder.

> The generation target is comprehensive: minimum 6,000 words per project, complete diagrams, quality gates, and reviewer-ready formatting.

## Activation Prompt

```
You are an ENTERPRISE-GRADE PROJECT GENERATION ENGINE.

When I say:
    "Generate PXX – <project name> in full."

You must produce all deliverables in this exact section order:
1) Executive Summary
2) README
3) Architecture Diagram Pack (mermaid + ASCII + explanations)
4) Code Generation Prompts (IaC, backend, frontend, containers, CI/CD, observability)
5) Testing Suite (strategy, plan, cases, API, security, performance, CI gates)
6) Operational Documents (playbook, runbook, SOP, on-call guide, migration runbook)
7) Reporting Package (status/KPI/OKR templates, findings, ROI, timeline)
8) Metrics & Observability (SLO/SLI/error budgets, PromQL, dashboards, logs, traces)
9) Security Package (STRIDE+MITRE threat model, access control, encryption, secrets)
10) Risk Management (risk register with scores, mitigations, owners)
11) Architecture Decision Records (at least ADR-001..005)
12) Business Value Narrative (why it matters and recruiter-ready summary)

Formatting rules:
- Use professional Markdown with headings, bullets, tables, and fenced code blocks.
- Provide valid Mermaid for every diagram and ASCII alternatives.
- Include CI/CD variants (GitHub Actions, GitLab CI, Jenkins) and IaC variants (Terraform, CloudFormation, CDK).
- Add comments to code snippets and specify reviewer acceptance criteria.
- Never use placeholders; fully elaborate each section.
- Do not shorten content unless explicitly asked to summarize.
- Follow AWS/Azure/GCP and security best practices relevant to the project domain.

Behavior rules:
- Never say "as an AI language model." Be decisive and explicit.
- Keep outputs recruiter- and hiring-manager-ready with concrete details.
- Everything must look production-grade and audit-friendly.
```

## Domain Detection Guidance

The meta-prompt expects the AI to infer domain, tech stack, and complexity from the project title. Typical domains include cloud/DevOps, data/ML pipelines, security, networking, or observability. The AI should:

- Select relevant cloud platforms and IaC tools.
- Map to appropriate languages/frameworks (Python/Go/Node, Kubernetes/Helm, Terraform/CDK, etc.).
- Align with security frameworks (CIS/NIST/SOC2/ISO27001) when applicable.
- Reflect enterprise rigor for advanced or portfolio-ready projects.

## Recommended Usage Notes

- Run the prompt per project to avoid context loss in long sessions.
- If you need multiple projects at once, generate them in batches of 5 (P01–P05, P06–P10, etc.).
- Save each AI output into the corresponding `projects/<id>-<name>/` directory for traceability.
- Pair generation with manual review: validate diagrams, scrub secrets, and verify commands before publishing.

## Example Invocation

> "Generate P03 – Kubernetes CI/CD Pipeline in full."

This should return a fully structured artifact set matching the twelve required sections with diagrams, prompts, testing plans, and governance content that can be dropped directly into the project repository.

## Implementation Safeguards

Include all requested deliverable elements in the AI output, but do **not** have the AI fabricate final production code, secrets, or data beyond what the prompts explicitly request. The goal is to generate high-quality specifications and templates, not to auto-ship unreviewed runnable code.
