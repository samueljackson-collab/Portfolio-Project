# Threat Model

Threats:
- Template injection
- Unsigned or tampered reports
- Queue backlog delaying delivery

Mitigations:
- Escape inputs and sandbox templates
- GPG signing + checksum verification
- Autoscale workers and retry policies
