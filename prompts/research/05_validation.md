# Validation & Reproducibility Checklist

Ensure that research outputs withstand scrutiny, can be independently reproduced, and invite constructive challenge.

## 1. Verification Workflow
1. **Source integrity**
   - Confirm URLs are live or archived, and citations include access dates.
   - Validate author credentials and check for known conflicts of interest.
2. **Evidence cross-checks**
   - Re-run key statistics or calculations to confirm reported numbers.
   - Compare claims across at least two independent sources when available.
3. **Timeline audit**
   - Verify that evidence aligns with the decision window; flag outdated references.
   - Note publication cadence for sources likely to update frequently (standards, vendor docs).
4. **Assumption testing**
   - Explicitly list assumptions and document how they were validated or why they remain open.

## 2. Reproducibility Steps
- Store research notes, claims tables, and citations in version control (Git/Markdown) with clear commit messages.
- Use standardized file names: `YYYY-MM-DD_topic_artifact-type.md`.
- Export search logs (queries, filters, platforms) as CSV or Markdown.
- Archive primary sources (PDF, transcript, dataset) in `artifacts/YYYY/MM/topic/` folders.
- Record tooling versions (browser extensions, scripts, language models) used during collection/analysis.
- For automated outputs, log prompts, parameters, and sampling seeds if applicable.

## 3. Red Team Challenge Prompts
Use these to intentionally stress-test the research before publishing.
- "What evidence could most easily invalidate our top recommendation?"
- "Which stakeholder would disagree with these findings, and what would they cite?"
- "If we had to brief an auditor tomorrow, what documentation would they request?"
- "Where might we have over-generalized from a single case study?"
- "How would a risk/compliance reviewer interpret our caveats?"

Document red-team findings and decisions in the research log.

## 4. Publication Readiness Gate
- [ ] All claims have at least one A/B-grade citation or a documented mitigation plan.
- [ ] Evidence grades and source types are recorded in the appendix.
- [ ] Counter-arguments reviewed and either incorporated or justified as out-of-scope.
- [ ] Validation notes appended to the final deliverable (date, reviewer, outcome).
- [ ] Reproducibility package (notes, logs, artifacts) stored in the designated repository folder.

Passing this gate signals that the dossier is ready for circulation or automation via the ResearchOrchestrator agent.
