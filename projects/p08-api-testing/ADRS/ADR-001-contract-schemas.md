# ADR-001: Adopt JSON Schema for Contract Tests

## Status
Accepted

## Context
API responses were previously validated via basic property checks. This was insufficient to detect subtle contract drift between environments.

## Decision
- Store JSON Schemas in `tests/schemas/` and enforce validation in Newman using the `ajv` plugin.
- Require schemas for every new endpoint before merging.

## Consequences
- CI fails when schemas missing or invalid.
- Documentation generated from schemas can be shared with backend teams.
- Slightly increased test execution time due to validation overhead.
