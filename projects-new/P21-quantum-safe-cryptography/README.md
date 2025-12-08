# P21 – Quantum-Safe Cryptography Lab

Showcases hybrid TLS and PQC experiments using OpenSSL oqsprovider and KEM key exchange.

## Quick start
- Stack: OpenSSL 3 + OQS provider, Docker, Python clients.
- Flow: Build openssl image with OQS, run demo server, execute clients negotiating hybrid ciphers and validate latency/compat.
- Run: make lint then pytest tests/test_handshakes.py
- Operate: Rotate test certificates weekly, track algorithm deprecations, and capture handshake traces.
