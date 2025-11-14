# AI Prompt List for Filling Portfolio Gaps

Curated set of ready-to-run AI prompts that accelerate delivery of the highest-priority assets identified in the **Portfolio Master Index**. Prompts are grouped by priority and map directly to the blockers called out in the latest assessment (GitHub visibility, visual evidence, missing READMEs, lack of hosted demos, resume tailoring, etc.).

Use these prompts with any advanced LLM (ChatGPT, Claude, Gemini) or image-generation model to quickly produce draft artifacts, which you can then refine and publish.

---
## 🔧 How to Use This Prompt Library
1. **Pick the gap** from the tables below (Critical → High → Medium priority).
2. **Copy the full prompt block** (everything inside the fenced code block) into your AI assistant.
3. **Replace bracketed placeholders** like `[PROJECT_ID]`, `[MERMAID_SNIPPET]`, or `[ROLE_TARGET]` with specifics from this repo.
4. **Paste the AI output** into the relevant project directory (see "Repo Target" column) and edit as needed before committing.
5. **Capture final evidence** (screenshots, rendered diagrams, etc.) and link them from project READMEs.

Tip: Chain prompts—use the README generator first, then pass that README back into the screenshot script prompt so the AI knows which views to capture.

---
## 🟥 Critical Gaps (Do This Week)
| # | Gap / Deliverable | Repo Target | Prompt |
|---|-------------------|-------------|--------|
| C1 | Publish homelab flagship project (README + assets) | `projects/06-homelab/PRJ-HOME-002/` | ```text
You are a senior systems engineer helping me publish my homelab project to GitHub.
Context:
- Homelab name: "Enterprise Homelab Infrastructure" (PRJ-HOME-002)
- Evidence available: Docker compose files, monitoring screenshots (to be captured), network segmentation write-up, backup automation scripts.
- Objectives: 1) Produce a GitHub-ready README with overview, architecture diagram section, services table, evidence checklist, and "How to Reproduce" instructions. 2) Outline recommended repo structure (folders for diagrams, screenshots, configs, runbooks).
Instructions:
1. Draft the README in Markdown with anchors for screenshots/diagrams so I can drop them in later.
2. Include sections for Highlights, Architecture, Security Controls, Backup & DR, Monitoring, and Next Steps.
3. Provide a bullet list of files I should export from this repo to populate the structure (reference existing docs when possible).
``` |
| C2 | GitHub Pages landing page (one-page portfolio site) | `frontend/portfolio-site/` (or `docs/` for Pages) | ```text
Act as a lead UX engineer tasked with converting my Portfolio Master Index into a single-page GitHub Pages site.
Deliverables: 1) Site map + content outline, 2) Tailwind/HTML component plan, 3) Hero + project cards copy.
Include sections for: Hero CTA, Featured Projects (Homelab, AWS Terraform, Observability), Interactive Mockups gallery, Resume links, Contact.
Output a Markdown table with each section, its purpose, key copy, and suggested React/Vite component if I choose to scaffold with VitePress later.
``` |
| C3 | Screenshot capture plan for 5 HTML mockups | `frontend/mockups/` | ```text
You are a creative director preparing a screenshot campaign for five interactive HTML mockups:
1. grafana-dashboard.html
2. wikijs-documentation.html
3. homeassistant-dashboard.html
4. proxmox-datacenter.html
5. nginx-proxy-manager.html
Tasks:
- Produce a shot list describing the exact viewport, resolution, and highlight callouts for each mockup.
- For every shot, write the caption text that will go into READMEs.
- Add a checklist of preparatory steps (browser zoom, light/dark mode, sample data) before capturing.
Return the plan as Markdown with subsections per mockup.
``` |
| C4 | Render architecture diagrams from Mermaid definitions | `docs/` + `projects/**/diagrams/` | ```text
You are a visualization specialist converting Mermaid diagrams into polished PNGs using an AI art tool.
Input: Paste the Mermaid code between <MERMAID> tags.
Output requirements:
1. Describe the diagram in natural language (topology, components, relationships).
2. Provide an AI image prompt (Midjourney/DALL·E) that recreates the diagram faithfully.
3. Suggest color palette and labeling tips so the final PNG matches enterprise standards.
Respond in Markdown with sections: "Diagram Summary", "AI Prompt", "Styling Notes".
<MERMAID>
[MERMAID_SNIPPET]
</MERMAID>
``` |
| C5 | Role-specific resumes (SDE, Cloud, DevOps, SRE, QA) | `professional/resume/` | ```text
You are an executive recruiter crafting five targeted resume outlines for the same engineer.
Roles: 1) System Development Engineer, 2) Cloud Engineer, 3) DevOps Engineer, 4) Site Reliability Engineer, 5) QA Automation Engineer.
For each role:
- Provide a 3-bullet professional summary tailored to that job family.
- List the top 6 skills/technologies to emphasize.
- Map 3 portfolio projects (by ID from this repo) to the resume's "Key Projects" section.
- Suggest measurable metrics or impact statements pulled from the Master Index.
Format each role under its own H3 heading.
``` |

---
## 🟧 High-Priority Gaps (This Month)
| # | Gap / Deliverable | Repo Target | Prompt |
|---|-------------------|-------------|--------|
| H1 | Terraform AWS infrastructure modules & README | `projects/01-sde-devops/PRJ-CLOUD-001/` | ```text
Act as a principal cloud engineer helping me finish PRJ-CLOUD-001 (AWS Terraform Infrastructure Platform).
Need: 1) Module breakdown (network, IAM, compute, observability), 2) Example `terraform.tfvars`, 3) README scaffolding with architecture narrative, testing strategy, and security considerations.
Use AWS best practices (multi-AZ, least privilege, tagging). Return Markdown sections I can drop directly into the project README, plus a file/folder checklist for module code.
``` |
| H2 | Publish interactive mockups to GitHub Pages | `frontend/mockups/` + `docs/mockups/` | ```text
You are a DevRel engineer preparing instructions to host five HTML mockups on GitHub Pages.
Deliverables:
1. Step-by-step deployment guide (branching, Actions workflow, directory layout).
2. Accessibility checklist for each mockup.
3. Embed code snippets (iframe) I can reuse inside READMEs.
Output everything as a numbered plan followed by copy-paste snippets.
``` |
| H3 | Demo video script (Homelab walkthrough) | `projects/06-homelab/PRJ-HOME-002/assets/video/` | ```text
Serve as a solutions architect writing a 3-minute video script for the Homelab Enterprise Infrastructure project.
Structure:
- Hook (15s)
- Problem statement (30s)
- Architecture walkthrough (90s)
- Reliability & security highlights (30s)
- Call-to-action (15s)
Include onscreen text cues, suggested B-roll, and narration.
Return as a table with timestamp, narration, visuals, and CTA notes.
``` |
| H4 | Top-5 project README generator | Relevant `projects/**/README.md` | ```text
Generate a reusable README template tailored for portfolio projects.
Sections required: Overview, Architecture Diagram, Stack, Key Decisions, Setup, Validation & Evidence, Next Iteration.
Provide short example content referencing Homelab, AWS Terraform, Observability Stack, Kubernetes CI/CD, and Resume Generator projects.
Deliver as Markdown with comments like <!-- Replace with project-specific details -->.
``` |
| H5 | GitHub Actions baseline for docs linting/build | `.github/workflows/docs.yml` | ```text
You are a DevOps engineer creating a GitHub Actions workflow that lints Markdown and builds static docs.
Requirements:
- Trigger on push + PR to `main` and `work/*` branches.
- Steps: checkout, setup Node 18, install `markdownlint-cli` + `remark`, run lint, run `npm run build-docs` (if script exists), upload artifact.
- Include concurrency control + job summary output.
Return the full YAML workflow.
``` |

---
## 🟨 Medium-Priority Gaps (Next 90 Days)
| # | Gap / Deliverable | Repo Target | Prompt |
|---|-------------------|-------------|--------|
| M1 | Kubernetes CI/CD migration plan | `projects/03-kubernetes-cicd/` | ```text
You are a platform architect drafting the migration plan from Docker Compose to K3s for the homelab services.
Deliverables: phased rollout plan, manifest inventory, GitOps workflow diagram description, risk register, and rollback strategy.
Reference services: Wiki.js, Immich, Home Assistant, Nginx Proxy Manager, Grafana stack.
Provide Markdown subsections for each deliverable.
``` |
| M2 | Observability stack standalone project | `projects/01-sde-devops/PRJ-OBS-015/` | ```text
Act as an SRE documenting a standalone Prometheus/Grafana/Loki stack project derived from the homelab.
Need: project overview, infra diagram description, docker-compose snippet, alert philosophy, SLO table, and evidence checklist.
Return a README-ready draft.
``` |
| M3 | Network segmentation showcase | `projects/06-homelab/PRJ-NET-001/` | ```text
You are a network architect building a case study for VLAN segmentation.
Prompt should produce: threat model summary, VLAN table (ID, CIDR, trust level, allowed flows), UniFi firewall rule examples, and troubleshooting FAQ.
Use existing VLANs (10,20,30,40,50) as baseline.
``` |
| M4 | QA automation starter kit | `projects/05-qa-automation/PRJ-QA-001/` | ```text
You are a QA lead asked to bootstrap an end-to-end automation project.
Need: test pyramid plan, tooling stack recommendation (Playwright, Pytest, GitHub Actions), sample test case (login flow), and CI integration steps.
Deliverable should read like a README first draft.
``` |
| M5 | Video tutorial series outline (15 episodes) | `docs/` or `professional/content/` | ```text
As a content strategist, design a 15-episode tutorial roadmap covering the entire portfolio.
For each episode: title, objective, prerequisites, assets to show (screenshots, diagrams), and CTA.
Organize episodes into three arcs (Foundations, Projects, Visibility).
``` |

---
## 🟦 Supporting Prompt Templates
- **Architecture Decision Records:**
```text
Create an ADR for decision [DECISION_NAME]. Context: [what problem]. Options considered: [Option A], [Option B], [Option C]. Document rationale, pros/cons, and revisit triggers.
```
- **Evidence Capture Checklist:**
```text
Generate a checklist of screenshots, logs, metrics exports, and diagram updates needed to prove completion of [PROJECT_ID]. Include column for "Status", "Asset Location", and "Notes".
```
- **Test Case Generator:**
```text
Produce a table of functional + non-functional test cases for [SERVICE] focusing on reliability, security, and performance. Include fields: ID, Scenario, Steps, Expected Result, Evidence to Capture.
```
- **Content Repurposing Prompt:**
```text
Summarize [DOCUMENT_NAME] into a 5-slide presentation outline with speaker notes, pull quotes, and metrics. Highlight why recruiters should care.
```

---
## 📌 Next Steps After Using the Prompts
1. Track outputs in `PROJECT_COMPLETION_CHECKLIST.md` to keep status accurate.
2. Add generated assets/screenshots to each project’s `assets/` directory and reference them in READMEs.
3. Commit early and often with descriptive messages (e.g., `docs: add homelab README scaffold from prompt kit`).
4. Once top 5 projects are published with evidence, update `README.md` and `PORTFOLIO_SUMMARY_TABLE.txt` with GitHub links.
5. Revisit this prompt library monthly—add new prompts for upcoming gaps (e.g., GitOps, QA frameworks, community outreach).
