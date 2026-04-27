# ADR-006: Portfolio-Wide Delivery Metrics

## Status
Accepted

## Context
Leadership needs a unified view of delivery health, including lead time, MTTR, deployment frequency, and coverage. The Master Factory summary prescribes an automated metric pack refreshed regularly to inform prioritization and risk decisions.

## Decision
Publish and maintain an automated metrics pipeline that aggregates delivery KPIs across projects. Standardize the metric definitions and update cadence, and expose the results through a shared dashboard consumable by engineering and leadership stakeholders.

## Consequences
- Decision-makers gain a consistent view of portfolio health and bottlenecks.
- Metric drift is reduced because definitions and refresh schedules are centralized.
- Engineering teams can benchmark improvements and target investments using shared KPIs.

## References
- Master Factory Deliverables Summary, item 6: Portfolio-Wide Delivery Metrics (docs/master_factory_deliverables.md)
