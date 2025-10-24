# Usage Guide

**Purpose:** Provide a comprehensive workflow for executing the Portfolio Documentation System from idea to published portfolio and job search readiness.

---

## 1. System Orientation

### 1.1 Key Documents at a Glance

| File | Purpose | Owners | Update Cadence |
| --- | --- | --- | --- |
| `README.md` | Entry point and high-level roadmap. | You | Quarterly review |
| `USAGE_GUIDE.md` | Day-to-day operating procedure for the entire system. | You | Update as processes evolve |
| `project_template.md` | Source template for project documentation. | You | Update when template improves |
| `soft_skills_framework.md` | Soft skill positioning strategies and evidence prompts. | You | Review monthly |
| `portfolio_structure.md` | Defines the five elite projects and sequencing. | You | Update as portfolio evolves |
| `recruiter_positioning.md` | Scripts, pitches, and objection handling. | You | Update during job search |
| `glossary_template.md` | Reusable glossary entry format. | You | Update when new terms appear |

### 1.2 Document Map

1. Start in `README.md` to align on principles and structure.
2. Use this `USAGE_GUIDE.md` to plan your execution cadence.
3. Duplicate `project_template.md` into each project folder.
4. Pull storytelling cues from `soft_skills_framework.md` when writing project narratives.
5. Reference `portfolio_structure.md` to maintain coherence between projects.
6. Practice messaging with `recruiter_positioning.md` before outreach and interviews.
7. Build or update glossary entries for each project using `glossary_template.md`.

---

## 2. Getting Started Quickly

### 2.1 Five-Step Quick Start (for Project #1)

1. **Select Project:** Use the Project Selection Matrix (Section 4.2) to choose the first project, typically Kubernetes Infrastructure.
2. **Create Workspace:** Copy `project_template.md` into `projects/PRJ-###/README.md` and adjust metadata.
3. **Define Outcomes:** Fill in the Executive Summary, Business Value, and Success Criteria sections first.
4. **Schedule Sprints:** Allocate four weekly milestones (implementation, documentation, operations, polish).
5. **Kickoff Session:** Spend 90 minutes outlining ADRs, risk register, and measurement plan before writing code.

### 2.2 Quick Wins in the First Week

- Complete the soft skills self-assessment to highlight existing strengths.
- Draft your elevator pitch from `recruiter_positioning.md`.
- Create a Trello/Notion board with cards mapped to the checklists in Section 5.
- Book feedback sessions with at least one technical mentor and one non-technical reviewer.

---

## 3. Workflow by Document

### 3.1 `project_template.md`

1. **Executive Summary First:** Define problem, solution, and business ROI in plain language.
2. **Architecture Decisions:** Document ADRs as soon as you make significant choices. Capture drivers, options, decisions, and consequences.
3. **Implementation Guide:** Write the detailed steps while actively building to avoid knowledge gaps.
4. **Operational Readiness:** Complete runbooks, monitoring dashboards, and disaster recovery plans before calling the project done.
5. **Soft Skill Sections:** Populate the seven soft skill narratives with specific anecdotes, metrics, and lessons.
6. **Validation & Testing:** Include automated test results, manual checklists, and success metrics.
7. **Polish:** Finalize troubleshooting, alternative approaches, ROI analysis, and career impact statement.

### 3.2 `soft_skills_framework.md`

- Use the STAR prompts and evidence tables to develop each soft skill story.
- Align project outcomes with the "Signals Recruiters Look For" checklists.
- Update self-assessment quarterly to maintain growth stories.

### 3.3 `portfolio_structure.md`

- Map each project to the target roles (Infrastructure, DevOps, Security, SRE).
- Maintain consistency in naming conventions and navigation.
- Use the expansion roadmap when adding new initiatives beyond the core five.

### 3.4 `recruiter_positioning.md`

- Rehearse the three elevator pitches weekly.
- Use objection handling scripts when tailoring outreach emails.
- Keep negotiation notes for each opportunity in the Offer Tracker (Section 7.3).

### 3.5 `glossary_template.md`

- Create glossary entries for every specialized term referenced in your portfolio.
- Link glossary entries from each project to support non-technical readers.
- Schedule quarterly reviews to expand or retire entries based on industry shifts.

---

## 4. Planning & Scheduling

### 4.1 Week-by-Week Schedule (20 Week Plan)

| Week | Theme | Key Deliverables |
| --- | --- | --- |
| 1 | Foundation | Read frameworks, select first project, set up tools, baseline elevator pitch. |
| 2 | Project 1 – Build | Implement core infrastructure/code, draft ADRs, capture screenshots. |
| 3 | Project 1 – Document | Fill template sections, document runbooks, gather metrics. |
| 4 | Project 1 – Operationalize | Conduct testing, run DR drills, finalize troubleshooting. |
| 5 | Project 1 – Polish | Peer reviews, integrate feedback, finalize ROI narrative. |
| 6 | Project 2 – Build | Repeat cycle for CI/CD pipeline; focus on automation evidence. |
| 7 | Project 2 – Document | Populate documentation with pipeline diagrams and guardrails. |
| 8 | Project 2 – Operationalize | Implement monitoring, rollback strategy, and audit trails. |
| 9 | Project 2 – Polish | Quality checks, update STAR stories, schedule review. |
| 10 | Project 3 – Build | Choose Security Hardening or Observability depending on goals. |
| 11 | Project 3 – Document | Emphasize threat modeling or observability metrics. |
| 12 | Project 3 – Operationalize | Execute tabletop exercises or dashboard validations. |
| 13 | Project 3 – Polish | Update recruiter messaging with new achievements. |
| 14 | Project 4 – Build | Start fourth project aligned to your target role. |
| 15 | Project 4 – Document | Highlight collaboration and cross-team communication. |
| 16 | Project 4 – Operationalize | Focus on runbooks and incident response integration. |
| 17 | Project 4 – Polish | Aggregate success metrics and update ROI calculator. |
| 18 | Portfolio Assembly | Create landing pages, navigation, cross-project comparison tables. |
| 19 | Interview Prep | Finalize pitches, run mock interviews, curate stories per role. |
| 20 | Job Search Launch | Outreach campaigns, application batching, negotiation prep. |

### 4.2 Project Selection Matrix

| Priority | Criteria | Questions to Ask |
| --- | --- | --- |
| Business Value | Demonstrates cost savings, revenue impact, or risk reduction. | What measurable outcome proves value to leadership? |
| Learning Agility | Requires new tools/skills you can showcase mastering quickly. | Which technologies will grow my capability fastest? |
| Storytelling Potential | Offers strong soft skill narratives (leadership, collaboration, adaptability). | Which experiences will impress behavioral interviewers? |
| Market Demand | Aligns with job descriptions for target roles. | What gaps do recruiters frequently mention? |
| Evidence Availability | Access to logs, screenshots, diagrams, or metrics to substantiate claims. | Can I gather proof without breaching confidentiality? |

---

## 5. Quality Checklists

### 5.1 Project Completion Checklist

- [ ] Executive summary communicates problem, solution, and business impact.
- [ ] ADRs capture at least three pivotal decisions with trade-off analysis.
- [ ] Implementation steps reproducible by an engineer with similar background.
- [ ] Runbook covers monitoring, alerts, escalation paths, and recovery drills.
- [ ] Testing documents include automated and manual validation evidence.
- [ ] ROI and cost analysis quantified with conservative, defensible numbers.
- [ ] Security considerations and risk mitigations documented clearly.
- [ ] Troubleshooting guide offers decision trees or flow charts.
- [ ] Soft skill sections populated with STAR-formatted stories.
- [ ] Career impact statement articulates skills gained and next steps.

### 5.2 Document Quality Checklist

- [ ] Plain-language summaries for executives and non-technical stakeholders.
- [ ] Consistent formatting (headings, tables, callouts) across all documents.
- [ ] Cross-links between projects, glossary entries, and supporting evidence.
- [ ] Visual assets exported into `assets/diagrams` or `assets/screenshots`.
- [ ] Accessibility considerations (alt text, color contrast) included.

### 5.3 Soft Skill Evidence Checklist

- [ ] Communication: Provide example of simplifying complexity for stakeholders.
- [ ] Leadership: Document how you drove alignment, made decisions, or delegated.
- [ ] Problem-Solving: Capture root cause analysis and structured reasoning.
- [ ] Learning Agility: Show rapid skill acquisition with timeline and proof.
- [ ] Business Acumen: Tie technical work to financial or strategic outcomes.
- [ ] Risk Management: Highlight threat modeling, controls, and contingency plans.
- [ ] Collaboration: Showcase knowledge sharing, pair sessions, or mentoring.

---

## 6. Common Pitfalls & How to Avoid Them

| Pitfall | Warning Signs | Prevention |
| --- | --- | --- |
| Underestimating Documentation Time | Template sections left blank near deadlines. | Schedule documentation days separately from build days. |
| Vague Business Impact | ROI section filled with generic statements. | Quantify metrics early; gather baselines before implementation. |
| Soft Skills as Afterthought | Stories added last minute without depth. | Draft soft skill notes during weekly retrospectives. |
| Overbuilding Scope | Multiple projects started without completion. | Limit active work-in-progress to one major project at a time. |
| Evidence Gaps | Missing screenshots/logs when writing final draft. | Capture evidence continuously; maintain an evidence folder. |
| Feedback Avoidance | No external reviews before declaring done. | Book review sessions when scheduling the project timeline. |

---

## 7. Progress Tracking & Integration with Job Search

### 7.1 Weekly Status Report Template

```
Week #: _______      Dates: ______________
Focus Area: (Build / Document / Operationalize / Polish / Assembly / Job Search)

Accomplishments:
- 
- 
- 

Metrics Updated:
- KPI / Baseline / Result
- KPI / Baseline / Result

Soft Skill Evidence Captured:
- Communication:
- Leadership:
- Learning Agility:

Blockers & Risks:
- 

Next Week Commitments:
- 
```

### 7.2 Project Kanban Board (Columns)

1. **Backlog** – Ideas, research tasks, resource gathering.
2. **In Progress** – Active build or documentation tasks.
3. **Review** – Items awaiting feedback or validation.
4. **Evidence Needed** – Screenshots, logs, metrics pending capture.
5. **Done** – Completed tasks validated against checklists.

### 7.3 Interview & Offer Tracker

| Company | Role | Stage | Key Stories to Highlight | Follow-Up Date | Notes |
| --- | --- | --- | --- | --- | --- |
| Example Corp | DevOps Engineer | Technical Screen | CI/CD pipeline automation, incident response tabletop. | 2025-05-18 | Sent thank-you email; waiting on feedback. |

Maintain this table within `recruiter_positioning.md` or export to a spreadsheet for daily review during the job search phase.

---

## 8. Integration with Job Search Activities

1. **Resume Alignment:** Tailor bullet points using the Success Metrics and ROI from each project; keep a master list in `final/`.
2. **Cover Letters & Outreach:** Pull language from soft skill sections to demonstrate leadership and adaptability.
3. **Interview Prep:** Use STAR stories crafted in project templates and the frameworks in `recruiter_positioning.md`.
4. **Negotiation:** Document quantified impacts (time saved, risk reduced) to justify target compensation.
5. **Portfolio Maintenance:** Update metrics and achievements quarterly to stay market-relevant.

---

## 9. Continuous Improvement

- Conduct a mini-retrospective after every project using the prompts in Section 7.1.
- Update templates with lessons learned and share improvements in `templates/`.
- Revisit `soft_skills_framework.md` quarterly to refresh stories and identify growth areas.
- Track revisions in a change log stored in `final/CHANGELOG.md`.

---

## 10. Support Resources

- **Community Feedback:** Share drafts with peers, mentors, or online communities focused on DevOps/SRE/Cloud.
- **Learning Library:** Maintain bookmarks or notes in `templates/` for recurring references (AWS docs, CNCF guides, etc.).
- **Accountability:** Pair with a study buddy or mentor for bi-weekly check-ins.
- **Health & Sustainability:** Schedule rest days and celebrate milestones to avoid burnout.

---

Use this guide as your operating manual. Revisit it weekly to ensure you are executing deliberately, capturing evidence continuously, and aligning each artifact with your overarching career narrative.

