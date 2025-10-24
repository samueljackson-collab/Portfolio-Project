# Reporting Frameworks

Translate research insights into consistent, decision-ready deliverables tailored for different stakeholder needs.

## 1. Standard Research Dossier Outline
1. **Cover Page & Metadata**
   - Title, topic owner, researcher(s), date, revision, confidentiality level.
   - Summary of research scope, timeframe, and key questions answered.
2. **Executive Summary**
   - 3–5 bullet highlights: problem framing, top findings, recommended next actions.
   - One-sentence risk statement capturing uncertainty or dependency.
3. **Key Findings**
   - Organized by theme; include claim statement, evidence summary, citation references.
   - Visual aids: tables, charts, or matrices where data-driven.
4. **Implications & Recommendations**
   - Decision options with pros/cons, resource estimates, and urgency level.
   - Implementation considerations and stakeholders affected.
5. **Risk & Counterpoints**
   - Document dissenting evidence, data gaps, and mitigation strategies.
6. **Next Steps & Research Backlog**
   - Outstanding questions, planned follow-up interviews, data requests.
7. **Appendix**
   - Methodology notes, search logs, extended tables, glossary.
   - Raw notes excerpt, annotated bibliography, and archived artifacts list.

## 2. Alternate Reporting Styles
- **Rapid Brief** (1–2 pages): use when stakeholders need a quick orientation.
  1. Overview
  2. Three key signals
  3. Risks/open questions
  4. Immediate actions
- **Deep Dive** (deck or long-form): use when delivering to technical or executive review boards.
  1. Context & objectives
  2. Methodology (search coverage, evidence grading)
  3. Detailed findings (per theme)
  4. Scenarios & forecasts
  5. Recommendations & roadmap
  6. Appendix (sources, interview notes)
- **Playbook Update**: integrate research into operational guides.
  1. Trigger/event
  2. Response workflow (with owner)
  3. Decision gates & metrics
  4. Reference materials

## 3. Reporting Quality Checklist
- [ ] Every claim maps to citations with evidence grade noted.
- [ ] Stakeholder-specific implications called out (Ops, Security, Exec, Legal, etc.).
- [ ] Risk section distinguishes known unknowns vs. assumptions.
- [ ] Visuals or tables captioned with data source and date.
- [ ] Summary includes recommended actions with priority and owner.
- [ ] Document version and change log appended for future reference.

## 4. Notes-to-Report Workflow
1. Export claims → evidence table from analysis phase.
2. Group claims by stakeholder decision impact and convert into prose.
3. Insert inline citations using `[Author, Year]` or footnotes per project standard.
4. Run a "red team" pass to challenge conclusions (see `05_validation.md`).
5. Finalize metadata, file naming (`YYYY-MM-DD_topic_report-type.md`), and storage location.

Consistency across reports makes it possible to automate packaging via `scripts/build_docs.*` and enables the ResearchOrchestrator agent to produce repeatable outputs.
