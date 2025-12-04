# Testing Strategy

## Objectives
- Validate DNS failover timing and correctness.
- Ensure data snapshot replication between regions.
- Confirm runbooks for promotion/demotion are accurate.

## Cases
| ID | Scenario | Expected |
|----|----------|----------|
| TC-MR-01 | Primary healthy | Traffic served from primary; latency baseline recorded. |
| TC-MR-02 | Primary failure | After health check failures, traffic shifts to secondary within 60s. |
| TC-MR-03 | Data sync | Snapshot copied to secondary bucket; checksum matches. |
| TC-MR-04 | Failback | After recovery, traffic restored to primary with minimal loss. |

## Execution
- Simulation: `python producer/failover_sim.py --fail-after 30` to induce failover.
- Validation: `python consumer/validate.py --report out/failover.json` checks latency, routing, and data sync flags.
- K8s smoke: apply `k8s/base.yaml` to create per-region services and test DNS policies via CoreDNS stub.
