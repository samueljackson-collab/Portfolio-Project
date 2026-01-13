# P21: Quantum-Safe Cryptography

PQ-safe key exchange demo with hybrid TLS posture checks.

## ⚠️ IMPORTANT DISCLAIMER

**This is a demonstration/educational implementation only.** The cryptographic operations in this project use placeholder code with `os.urandom()` for illustration purposes.

**For production use:**
- Use a real post-quantum cryptography library like [liboqs](https://github.com/open-quantum-safe/liboqs)
- Implement NIST-approved PQC algorithms (CRYSTALS-Kyber, CRYSTALS-Dilithium, etc.)
- Follow current cryptographic best practices and security guidelines
- Conduct thorough security audits before deployment

This implementation is NOT quantum-resistant and should NOT be used for any security-critical applications.

## What this pack includes
- Standard documentation set (architecture, testing, playbook, SOP, RUNBOOKS, ADRS, THREAT_MODEL, RISK_REGISTER).
- A tiny producer/job/consumer pipeline to demonstrate executable artifacts.
- Kubernetes deployment stub showing how to package the worker.

## Quick start
```bash
cd /workspace/Portfolio-Project/projects-new/P21-quantum-safe-cryptography
python docker/producer/main.py --validate
python docker/producer/main.py --payload '{"event":"demo"}'
```

## Deliverables
- Evidence files land in `artifacts/` for easy inspection.
- Report templates are stored in `REPORT_TEMPLATES/`.
- Metrics guidance captured under `METRICS/`.
