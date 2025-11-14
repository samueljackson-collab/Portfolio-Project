# AI Prompt List for Portfolio Gaps

Use these prompts when you need help drafting or expanding portfolio artifacts. They are grouped by priority based on the portfolio gap analysis. Each prompt assumes access to the repository so the assistant can cite the correct files.

## Critical Priority

1. **Homelab Runbook Deep Dive**
   - *Prompt*: "You are an SRE editor. Review `projects/23-advanced-monitoring` and draft a step-by-step incident runbook that reinforces the 15-minute MTTR target. Include pre-checks, command snippets, and rollback criteria."
2. **Cost Benchmark One-Pager**
   - *Prompt*: "Summarize the 95% cost savings narrative using data from `Portfolio_Master_Index_COMPLETE.md` and `Portfolio_Master_Index_CONTINUATION.md`. Produce a one-page executive brief with charts or ASCII tables where appropriate."
3. **Zero-Trust Architecture Explainer**
   - *Prompt*: "Explain the five-VLAN zero-trust layout (Section 4.1.3) to a CISO. Highlight ACL enforcement, identity controls, and monitoring hooks."

## High Priority

1. **Automation ROI Case Study**
   - *Prompt*: "Draft a case study describing how 480 hours/year of toil were eliminated. Reference GitHub Actions workflows, Ansible playbooks, and Terraform modules."
2. **Observability Dashboard Walkthrough**
   - *Prompt*: "Create a narrated walkthrough of the Grafana dashboards (Section 4.1.8) that proves the 15-minute MTTR. Include which panels to show in a live demo."
3. **Incident Simulation Summary**
   - *Prompt*: "Summarize the credential-compromise tabletop (Section 8.2 in the continuation index). Detail triggers, responders, and remediation timeline."

## Medium Priority

1. **Learning Roadmap Update**
   - *Prompt*: "Using `PORTFOLIO_COMPLETION_PROGRESS.md`, propose the next three learning OKRs with metrics, artifacts, and links to supporting repositories."
2. **Stakeholder Outreach Email**
   - *Prompt*: "Write a recruiter-friendly email that highlights the top 10 metrics from `Portfolio_Navigation_Guide.md`."
3. **Automation Backlog Grooming**
   - *Prompt*: "Read `scripts/` and `enterprise-portfolio/` directories and suggest two automation enhancements that further reduce MTTR."

## Usage Tips
- Always include citations back to the relevant Markdown file or repository path when using generated content.
- Keep the MTTR (15 minutes) and cost savings (95%) figures consistent across all AI-assisted drafts.
- Store outputs in `/reports` or `/docs` with a clear filename that matches the artifact you generated.
