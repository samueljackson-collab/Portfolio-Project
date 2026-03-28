# ADR-005: Documentation & Knowledge Hub

## Status
Accepted

## Context
Documentation was fragmented across projects, complicating onboarding and coordination. The Master Factory summary calls for a centralized knowledge hub where guides, indexes, and ADRs are discoverable and linked from root documentation.

## Decision
Create and maintain a documentation hub that consolidates guides, indexes, and ADRs. All new documents must be linked from the root indexes, and ADRs should reside in a dedicated `adr/` directory with consistent naming and status tracking.

## Consequences
- Contributors can quickly locate authoritative guidance during delivery.
- Decision traceability improves because ADRs are centralized and referenced in indexes.
- Documentation updates become part of the definition of done for new workstreams.

## References
- Master Factory Deliverables Summary, item 5: Documentation & Knowledge Hub (docs/master_factory_deliverables.md)
