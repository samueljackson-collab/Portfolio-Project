---
name: Feature request
about: Suggest an enhancement or new capability
labels: ["enhancement"]
---

## Summary
Provide a concise, one-sentence description of the requested feature.

## Problem Statement
What problem are we solving or opportunity are we addressing?

## Goals
- Goal 1
- Goal 2

## Non-Goals
- Out of scope item 1

## Proposed Solution
Describe the preferred approach, including any technical details.

## Alternatives Considered
List other approaches and why they were not chosen.

## Dependencies
List any dependencies, services, or data required.

## Risks/Tradeoffs
Call out potential downsides or constraints.

## Success Metrics
How will we measure success?

## Acceptance Criteria
- [ ] Feature meets the stated goals
- [ ] Documentation updated (if applicable)
- [ ] Tests or validation updated (if applicable)

---

## Example (completed)

**Summary**
Add a portfolio-wide status dashboard that aggregates project health checks.

**Problem Statement**
Reviewers must open each project README to understand current status, which is time-consuming during demos.

**Goals**
- Provide a single page that lists project status, last deployment, and health.
- Enable quick filtering by project category (e.g., security, cloud, QA).

**Non-Goals**
- Building a full analytics platform or historical SLA reporting.

**Proposed Solution**
Create a `portfolio-status` page in `docs/` that pulls data from a JSON index updated by a nightly workflow. Surface the link in `DOCUMENTATION_INDEX.md` and the root `README.md`.

**Alternatives Considered**
- Manual spreadsheet updates (rejected due to staleness).
- Embedding status into each README only (rejected due to discoverability).

**Dependencies**
- GitHub Actions workflow to generate the JSON index.
- Standardized metadata files per project.

**Risks/Tradeoffs**
- Requires ongoing maintenance of metadata across projects.

**Success Metrics**
- Dashboard loads in under 2 seconds.
- At least 90% of projects report status without missing fields.

**Acceptance Criteria**
- [ ] `docs/portfolio-status.md` rendered and linked from the docs hub
- [ ] Workflow updates JSON index nightly
- [ ] README links updated to include the dashboard
