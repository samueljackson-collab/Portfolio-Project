# AI Prompt Execution Framework

## Master Guide to Using AI for Portfolio Completion (Part 3 of 3)

**Part 1:** `AI_PROMPT_LIBRARY.md` (Critical & High prompts)  
**Part 2:** `AI_PROMPT_LIBRARY_MEDIUM_LOW.md` (Medium & Low prompts)

This playbook covers execution strategies, quality control, and best practices so every AI-assisted deliverable ships production-ready, with **complete, runnable deliverables** as the default definition of success.

---

## 📋 Executive Summary

This framework is the operational handbook for maximizing AI productivity. It explains how to:
- Cut portfolio completion time from 200+ hours to ~80-100 hours
- Maintain consistent professional quality
- Avoid common AI pitfalls
- Batch and schedule work efficiently
- Build a reusable prompt library for ongoing updates

---

## 🎯 Core Execution Principles

**Default success criterion:** Every task produces a complete, runnable deliverable with a clear startup recipe (directory map, entry points, sample data, and run command).

### Principle 1: Treat Prompts Like Code
- Be explicit: context, requirements, constraints, examples
- Show desired format and style
- Include negative examples (what to avoid)
- Iterate on prompts based on output quality

### Principle 2: Iterate Relentlessly
1. Generate first draft
2. Review gaps/inaccuracies
3. Refine prompt with precise feedback
4. Regenerate and compare
5. Manually polish for final pass

### Principle 3: AI Drafts, Humans Ship
- AI handles ~70% (drafting); human reviews ~30%
- Always verify technical accuracy, personalization, and formatting
- Never publish without testing code, checking links, and proofreading

### Principle 4: Design for Runnable Delivery
- Define the startup recipe before drafting (directory map, primary entry points, sample data, and run command)
- Keep instructions adjacent to code so handoffs stay frictionless
- Require smoke tests to prove the deliverable runs as documented

---

## 🛠️ Tool Selection Guide

| Tool | Best For | Strengths | Use Cases |
|------|----------|-----------|-----------|
| **Claude** | Long-form docs, complex projects | Huge context window, structured output | Architecture docs, comprehensive READMEs |
| **ChatGPT** | Quick iterations, code snippets | Fast responses, creative ideas | README drafts, blog outlines, scripts |
| **GitHub Copilot** | Inline coding assistance | IDE integration, context aware | Function implementation, tests |
| **Gemini** | Research & fact-checking | Web access, real-time info | Verifying best practices, current trends |

> Tip: Run multiple tools in parallel (different browser tabs) to speed up large tasks.

---

## 🔄 Batch Processing Strategy

### Why Batch?
- Maintain context and tone
- Reduce context-switching overhead
- Reuse prompt templates
- Accelerate review cycles

### Example Workflow: README Batch
1. Prepare template + required data per project
2. Generate drafts for 3-5 projects sequentially
3. Review all drafts in one sitting
4. Apply consistent polish (tone, formatting)
5. Add the startup recipe (directory map, entry points, sample data, run command)
6. Commit documents together

### Prompt Template Structure
```
Create a production-ready README for {{PROJECT_NAME}}.

PROJECT DETAILS:
- Purpose: {{PURPOSE}}
- Tech stack: {{TECH_STACK}}
- Key metrics: {{METRICS}}
- Target audience: {{AUDIENCE}}

[Standard instructions continue...]
```

---

## ✅ Quality Control Procedures

### Three-Pass Review
1. **Technical Accuracy** – test commands, verify versions, validate links
2. **Completeness & Consistency** – ensure every prompt requirement is met, no placeholders remain, and the startup recipe is present
3. **Polish & Professionalism** – grammar, tone, formatting, metrics

### Automated Checks
```bash
markdownlint **/*.md
markdown-link-check README.md
aspell check README.md
terraform fmt -check && terraform validate
yamllint k8s/**/*.yaml
pytest
```

Set up `.pre-commit-config.yaml` to run linting automatically before each commit.

---

## 🚀 Startup Recipe & Deliverable Checklist

Every deliverable should include a concise startup recipe that proves it runs end-to-end:
- **Directory map:** Show top-level folders, config locations, and where to place secrets
- **Entry points:** Identify commands (e.g., `main.py`, `npm start`, `docker compose up`) and any service URLs
- **Sample data:** Provide fixtures, example `.env` values, or seed scripts to unblock first run
- **Run command:** Single copy-paste command with prerequisites noted (tool versions, ports)

Deliverable readiness checklist (attach to prompts and reviews):
- [ ] Startup recipe documented next to the deliverable
- [ ] Commands executed successfully in a clean environment
- [ ] Inputs/outputs captured (screenshots, logs, or test artifacts)
- [ ] Rollback/cleanup notes recorded when applicable

Treat missing startup details as blockers—no deliverable is “done” until it is runnable by another teammate.

---

## 🚫 Common AI Pitfalls & Fixes

| Pitfall | Example | Prevention |
|---------|---------|------------|
| Invented features | Non-existent CLI flags | Cross-check docs; instruct AI to omit uncertain info |
| Outdated data | Legacy commands | Verify against latest docs; specify "as of Nov 2025" |
| Generic fluff | "Robust and scalable" statements | Demand specific metrics and facts |
| Formatting drift | Inconsistent headers/bullets | Provide style rules and run linters |
| Security issues | Hardcoded secrets | Require env vars + .env files, review manually |

---

## 🔧 Output Refinement Techniques

1. **Chained Prompting** – Architecture → Implementation → Documentation
2. **Comparative Prompting** – Generate multiple variations, merge best parts
3. **Incremental Enhancement** – Add complexity in phases (basic → advanced → production-ready)
4. **Example-Driven** – Provide best-in-class sample; request similar output
5. **Multi-Agent Review** – Optimist generates, Critic reviews, Pragmatist refines
6. **Recursive Improvement** – Have AI critique and improve its own output

---

## ⏱️ Time Estimates & Scheduling

| Deliverable | AI Time | Review | Testing | Total |
|-------------|--------:|-------:|--------:|------:|
| Simple README | 10m | 15m | 5m | 30m |
| Complex README | 20m | 30m | 10m | 60m |
| Blog Post | 15m | 30m | 5m | 50m |
| Docker Compose | 15m | 20m | 30m | 65m |
| Terraform Module | 30m | 45m | 60m | 135m |
| Architecture Doc | 45m | 60m | 15m | 120m |
| Test Suite | 60m | 30m | 60m | 150m |

Use time-boxing (Pomodoro) and energy-aware scheduling (creative work in mornings, reviews later).

---

## 📚 Prompt Library Organization

Structure your personal prompt repo:
```
my-prompts/
├── documentation/
├── code/
├── content/
└── examples/
```
Each template should include purpose, best tool, time estimate, prompt text with variables, post-processing checklist, and sample output links.

Track usage in a spreadsheet (date, task, tool, prompt ID, time spent, quality rating) to refine processes over time.

---

## ✅ Final Publishing Checklist

**Technical**
- [ ] Code/commands tested
- [ ] Links verified
- [ ] Versions current
- [ ] Startup recipe (directory map, entry points, sample data, run command) included and validated

**Content**
- [ ] All sections complete
- [ ] Specific metrics included
- [ ] Grammar/tone polished

**Security**
- [ ] Secrets externalized
- [ ] Sensitive data removed
- [ ] Dependencies reviewed

**Presentation**
- [ ] Screenshots/diagrams added
- [ ] Cross-links to related work
- [ ] CTA and contact info present

---

## 🎯 Next Steps
1. Review Parts 1-3 of the prompt library
2. Select top 5 prompts to execute this week
3. Set up prompt templates + quality checks
4. Block focused time for AI-assisted sprints
5. Track outcomes and iterate on prompts

**Remember:** AI handles the heavy lifting, but your expertise ensures accuracy, authenticity, and impact. Execute with rigor and your portfolio will stand out. 🚀
