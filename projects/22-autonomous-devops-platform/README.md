# Project 22: Autonomous DevOps Platform

## Overview
Event-driven automation layer that reacts to telemetry, triggers remediation workflows, and coordinates incident response using Runbooks-as-Code.

## Run
```bash
pip install -r requirements.txt
python src/autonomous_engine.py
```

## Assets
- Core automation engine in [`src/autonomous_engine.py`](src/autonomous_engine.py) with operational procedures in [`RUNBOOK.md`](RUNBOOK.md) and context in [`wiki/overview.md`](wiki/overview.md).
- CI workflow [`./.github/workflows/ci.yml`](.github/workflows/ci.yml) running pytest checks in [`tests/test_autonomous_engine.py`](tests/test_autonomous_engine.py).
- Kubernetes operator deployment for event ingestion in [`k8s/runbook-operator.yaml`](k8s/runbook-operator.yaml).
- Monitoring alerts for automation health in [`monitoring/alerts.yml`](monitoring/alerts.yml).
