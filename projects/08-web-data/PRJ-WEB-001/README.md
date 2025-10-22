# Commercial E-commerce & Booking Systems Portfolio

## Objective
- Recreate the evidence pack for the three commercial web projects (resort booking, high-SKU flooring, and tours marketplace) highlighting data workflows, automations, and operational playbooks.
- Provide contributor guidance for refreshing screenshots, anonymized datasets, and QA/regression artifacts that prove repeatability.

## Key Artifacts to Produce
- [ ] **Solution Overview Diagram** – front-end, CMS, payment gateways, and integration touchpoints for each client ([Coming Soon](./artifacts/solution-overview.md)). *(Target format: draw.io + PDF summary)*
- [ ] **Data Flow & ETL Workbook** – catalog update process, pricing imports, and validation queries ([Coming Soon](./workbooks/data-flow.md)). *(Target format: spreadsheet export with SQL snippets)*
- [ ] **Operational Runbook** – publishing cadence, content review, and incident triage steps ([Coming Soon](./runbooks/operations.md)).
- [ ] **QA Regression Checklist** – smoke/regression tests for booking flows, search, and pricing ([Coming Soon](./checklists/qa-regression.md)).
- [ ] **Analytics & KPI Dashboard Outline** – traffic, conversion, and booking metrics with owners ([Coming Soon](./dashboards/kpi-outline.md)).
- [ ] **Client Evidence Packet Index** – sanitized screenshots, testimonials, and deployment history ([Coming Soon](./evidence/client-packet.md)).

## Current Backfill Status
- Status: 🔵 **Planned** – prior documentation stored in client-specific Google Drives; nothing migrated to Git yet.
- Owner: Sam Jackson
- Target Backfill Window: 2025-05

## Recovery Dependencies & Blockers
- [ ] Obtain written approval from clients to reuse sanitized assets. *(Dependency: pending outreach emails sent 2025-01-22.)*
- [ ] Rebuild anonymized datasets from last export. *(Blocked until access to legacy VPS backups is restored; coordinate with hosting provider.)*
- [ ] Capture updated UI screenshots in staging environments. *(Dependency: rebuild staging containers using IaC from PRJ-SDE-001 once available.)*

## Coordination Notes
- Align QA checklist format with the standards defined in `projects/04-qa-testing/PRJ-QA-001` to keep testing artifacts consistent.
- Once data pipeline notebook is ready, cross-link with future automation work in `projects/07-aiml-automation/PRJ-AIML-001` for reuse.
