# Threat Model — P07

## Assets
- Simulation configs (`config/roaming.yaml`), synthetic subscriber database, PCAP artifacts, billing event logs.

## Entry Points
- CLI invocation (`make run-simulation`), exporter HTTP endpoint (port 9107), docker compose network.

## Threats
- **Tampered configs:** malicious MCC/MNC to bypass guardrails.
- **Credential leakage:** `.env` checked into logs/artifacts.
- **PCAP exposure:** packet captures leaked externally.
- **Denial of simulation:** toxiproxy/latency injection left enabled in CI.

## Mitigations
- Validate configs against schema; reject unknown MCC/MNC unless `ALLOWLIST_OVERRIDE` set.
- Add pre-commit hook scanning for secrets; `.env` excluded via `.gitignore`.
- PCAP scrubber removes IMSI/MSISDN; access restricted to engineers.
- CI toggles chaos only for dedicated jobs; default disabled.

## Residual Risks
- Synthetic data still resembles telecom flows; treat PCAP handling carefully.
- Metrics endpoint unauthenticated in dev; restrict network exposure.
