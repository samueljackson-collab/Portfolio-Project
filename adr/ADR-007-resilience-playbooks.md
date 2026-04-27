# ADR-007: Resilience & Recovery Playbooks

## Status
Accepted

## Context
Incident response practices vary across projects, increasing recovery times and operational toil. The Master Factory summary directs teams to deliver standard backup, restore, failover, and chaos-testing playbooks that align with shared architectures.

## Decision
Publish resilience playbooks covering backup/restore, failover patterns, and chaos drills for the portfolio’s common architectures. Teams must adopt the playbooks and integrate recovery steps into on-call runbooks and readiness reviews.

## Consequences
- Recovery times decrease because responders follow consistent, validated steps.
- Chaos exercises reinforce readiness and reveal gaps before incidents occur.
- Post-incident reviews can map remediation directly to shared playbook updates.

## References
- Master Factory Deliverables Summary, item 7: Resilience & Recovery Playbooks (docs/master_factory_deliverables.md)
