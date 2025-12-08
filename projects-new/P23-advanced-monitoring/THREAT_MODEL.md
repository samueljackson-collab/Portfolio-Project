# Threat Model

Threats:
- Synthetic credentials leakage
- Alert fatigue from flaky probes
- Collector overload

Mitigations:
- Store tokens in vault
- Use multiple vantage points and jitter
- Autoscale collectors and set sampling rules
