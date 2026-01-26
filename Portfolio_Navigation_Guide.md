# Portfolio Navigation Guide

Use this guide to move between the numerous survey, analysis, and infrastructure documents without losing context. Every section contains exact file paths so you can jump straight to the right artifact from the command line or the GitHub UI.

---

## 1. Quick Entry Points

| Scenario | Start Here | Why |
| --- | --- | --- |
| Need executive talking points | `SURVEY_EXECUTIVE_SUMMARY.md` | Contains KPIs, completion tiers, and stakeholder-ready messaging. |
| Need per-project facts | `PORTFOLIO_SURVEY.md` | Includes README text, tech stacks, and completion status for all 25 projects. |
| Need remediation steps | `IMPLEMENTATION_ANALYSIS.md` | Breaks down missing components, priorities, and effort ranges. |
| Need technology mapping | `TECHNOLOGY_MATRIX.md` | Consolidates dependencies, install guides, and quick start commands. |
| Need progress dashboards | `PORTFOLIO_COMPLETION_PROGRESS.md` | Converts the survey into measurable milestones. |

---

## 2. Navigating by Repository Area

1. **Root Documentation**  
   Files such as `DOCUMENTATION_INDEX.md`, `PORTFOLIO_GAP_ANALYSIS.md`, and `PORTFOLIO_VALIDATION.md` live at the repository root for instant discovery.
2. **`docs/` Folder**  
   Long-form references (`COMPREHENSIVE_PORTFOLIO_IMPLEMENTATION_GUIDE.md`, `HOMELAB_ENTERPRISE_INFRASTRUCTURE_VOLUME_2.md`) and handbooks under `docs/PRJ-MASTER-*` reside here.
3. **Project Implementations**  
   Browse `projects/` for numbered directories (`01-*` through `25-*`). Each contains `README.md`, runbooks, and architecture diagrams for the specific solution.
4. **Productized Sites**  
   - `portfolio-website/` → VitePress portal with rendered docs.  
   - `enterprise-portfolio/wiki-app/` → Next.js/React wiki for enterprise publishing.
5. **Automation**  
   - `infrastructure/`, `terraform/` → IaC definitions.  
   - `scripts/` → Shell utilities, e.g., `setup-portfolio-infrastructure.sh` with embedded quick navigation instructions.

---

## 3. CLI Shortcuts

```bash
# List the five highest-priority documents
git ls-files SURVEY_EXECUTIVE_SUMMARY.md PORTFOLIO_SURVEY.md \
  IMPLEMENTATION_ANALYSIS.md TECHNOLOGY_MATRIX.md DOCUMENTATION_INDEX.md

# Preview a document quickly
bat PORTFOLIO_SURVEY.md | head -n 120

# Jump directly to a project folder
cd projects/25-portfolio-website && ls
```

> **Note:** The `bat` command is optional; fall back to `sed -n '1,120p' FILE` if unavailable.

---

## 4. Decision Tree

1. **What do you need?**
   - **Metrics or KPIs?** → `SURVEY_EXECUTIVE_SUMMARY.md` and `PORTFOLIO_COMPLETION_PROGRESS.md`
   - **Technical gaps?** → `IMPLEMENTATION_ANALYSIS.md` + `CODE_ENHANCEMENTS_SUMMARY.md`
   - **Testing coverage?** → `TEST_SUITE_SUMMARY.md`, `TEST_GENERATION_COMPLETE.md`
   - **Deployment readiness?** → `FOUNDATION_DEPLOYMENT_PLAN.md`, `DEPLOYMENT_READINESS.md`
2. **Need a guided tour?**
   - Use this navigation guide in tandem with `Portfolio_Master_Index_COMPLETE.md` and `Portfolio_Master_Index_CONTINUATION.md`.
3. **Need visuals?**
   - Open `PORTFOLIO_ARCHITECTURE_DIAGRAMS_COLLECTION.md` or browse `assets/`.

---

## 5. Maintenance

- Update the quick entry table when any primary document is renamed or replaced.
- Confirm CLI examples stay accurate after structural changes.
- Cross-link new resources inside the decision tree to keep onboarding smooth.
