# Project 13: Advanced Cybersecurity Platform

## Overview
Security orchestration and automated response (SOAR) engine that consolidates SIEM alerts, enriches them with threat intel, and executes playbooks.

## Features
- Modular enrichment adapters (VirusTotal, AbuseIPDB, internal CMDB).
- Risk scoring model that accounts for asset criticality and historical incidents.
- Response automations (isolation, credential rotation, ticketing) executed via pluggable backends.

## Usage
```bash
pip install -r requirements.txt
python src/soar_engine.py --alerts data/alerts.json
```
