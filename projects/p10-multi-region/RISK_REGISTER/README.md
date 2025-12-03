# Risk Register — P10

| ID | Risk | Impact | Likelihood | Owner | Mitigation | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | DNS failover misroutes traffic | High | Medium | SRE | Policy tests + staged rollouts | Open |
| R2 | Replica lag causes data loss | High | Medium | DBA | Lag alerting; block failover when lag > threshold | Open |
| R3 | Terraform state exposed | High | Low | Dev Lead | Encrypted backend + least-priv IAM | Mitigated |
| R4 | S3 replication backlog | Medium | Low | Ops | Monitor backlog metric and increase bandwidth | Open |
