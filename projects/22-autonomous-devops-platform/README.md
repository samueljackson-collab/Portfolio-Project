# Project 22: Autonomous DevOps Platform

## Overview
Event-driven automation layer that reacts to telemetry, triggers remediation workflows, and coordinates incident response using Runbooks-as-Code.

## Architecture
- **Context:** Telemetry, alerts, and incidents must trigger consistent remediation steps with approvals, chat coordination, and auditability.
- **Decision:** Feed logs/metrics into an anomaly detector and policy engine that chooses actions, then orchestrate runbooks through workflow runners with ChatOps and CMDB approval gates.
- **Consequences:** Delivers rapid, consistent operations responses, but requires guardrails to prevent noisy signals from triggering unnecessary automation.

[Mermaid source](assets/diagrams/architecture.mmd) · Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

## Run
```bash
pip install -r requirements.txt
python src/autonomous_engine.py
```
