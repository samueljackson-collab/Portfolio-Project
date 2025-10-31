# Architecture

## Overview
Scheduled collectors gather evidence into a normalized store, while workflow engines manage approvals and package delivery.

## Component Breakdown
- **Evidence Collectors:** Pull configuration states, policies, and logs from systems of record.
- **Normalization Layer:** Transforms raw data into standardized control artifacts with metadata.
- **Workflow Engine:** Routes evidence for review, exception handling, and sign-off.
- **Audit Portal:** Provides dashboards and secure download links for auditors.

## Diagrams & Flows
```text
Collectors -> Normalization Store -> Workflow Engine -> Audit Portal -> Auditors
            Exception Queue -> Control Owners -> Resolution -> Updated Evidence
```
