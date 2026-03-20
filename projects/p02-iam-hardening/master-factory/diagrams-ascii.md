# Diagram Appendix (ASCII) — P02 IAM Hardening Master Factory

ASCII renditions complement the Mermaid diagrams to support quick reviews in terminals and tickets.

## System Flow
```
[Engineer]
   |
   v
[Policy PR] -> (make validate-policies) -> (make simulate) -> [Access Analyzer]
                                                   |                 |
                                                   |<-- fixes ------+
                                                   v
                                           [MFA enforcement]
                                                   |
                                   [Observability + Reporting]
                                                   |
                                   [Unused credential cleanup]
```

## CI/CD Flow
```
Repo -> CI `make setup`
        -> `make validate-policies`
        -> `make policy-diff`
        -> `make simulate` -> Access Analyzer -> MFA tests -> Approval -> Release
```

## IaC Flow
```
IaC templates -> Lint -> `make validate-policies` -> `make policy-diff` -> `make simulate`
        -> Terraform plan -> Access Analyzer -> MFA session enforcement -> Apply
        -> External access detection -> Credential cleanup -> Metrics/Alerts
```
