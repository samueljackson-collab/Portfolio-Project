# Project 13: Advanced Cybersecurity Platform

## Overview
Security orchestration and automated response (SOAR) engine that consolidates SIEM alerts, enriches them with threat intel, and executes playbooks.

## Architecture
- **Context:** Disparate alerts from SIEM/EDR feeds must be normalized, enriched, risk-scored, and turned into consistent actions across network, identity, and ticketing systems.
- **Decision:** Centralize ingest, enrichment adapters, and risk scoring inside the SOAR pipeline, then drive automated playbooks that update CMDB, rotate credentials, and isolate assets while logging every action.
- **Consequences:** Accelerates triage and response with measurable playbook outcomes, but depends on high-fidelity integrations and strong auditing to maintain trust.

[Mermaid source](assets/diagrams/architecture.mmd) · Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

## Features
- Modular enrichment adapters (VirusTotal, AbuseIPDB, internal CMDB).
- Risk scoring model that accounts for asset criticality and historical incidents.
- Response automations (isolation, credential rotation, ticketing) executed via pluggable backends.

## Usage
```bash
pip install -r requirements.txt
python src/soar_engine.py --alerts data/alerts.json
```
