# P07 International Roaming Simulation

This pack provides production-grade documentation and runnable assets for simulating cross-carrier roaming events. It mirrors the artifact layout from the P06 prompt pack so teams can drop it into CI/CD, tabletop exercises, or lab environments without additional scaffolding.

## Scope
- Synthetic call/data session generation for multi-operator roaming.
- Latency/loss injection to reproduce real-world impairments.
- K8s/Compose manifests for ephemeral labs.
- Operational guides (playbooks, runbooks, SOPs) and risk/threat coverage.

## Quickstart
1. Build and run the simulator locally:
   ```bash
   make -C projects/p07-roaming-simulation setup
   python producer/main.py --profile urban --events 200
   python consumer/main.py --ingest-file out/events.jsonl
   ```
2. Compose-based stack:
   ```bash
   docker compose -f docker/compose.roaming.yaml up --build
   ```
3. Kubernetes dry run:
   ```bash
   kubectl apply -k k8s/overlays/dev --dry-run=client
   ```

## Contents
- Architecture overview under `ARCHITECTURE/` with traffic flows and control-plane notes.
- Testing strategy and case matrix under `TESTING/`.
- Ready-to-use report templates for incident, drill, and QoS reviews under `REPORT_TEMPLATES/`.
- Operational docs: `PLAYBOOK/`, `RUNBOOKS/`, `SOP/`.
- Observability and SLO guidance in `METRICS/`.
- Decision log in `ADRS/`, threat model in `THREAT_MODEL/`, and project risk register in `RISK_REGISTER/`.
- Runnable samples in `docker/`, `producer/`, `jobs/`, `consumer/`, and `k8s/`.
