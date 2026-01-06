# Architecture

Stack: OpenSSL 3 + OQS provider, Docker, Python clients.

Data/Control flow: Build openssl image with OQS, run demo server, execute clients negotiating hybrid ciphers and validate latency/compat.

Dependencies:
- OpenSSL 3.0+ with liboqs-based OQS provider for post-quantum algorithm support.
- Docker 20.10+ for containerized OpenSSL builds and isolated test environments.
- Python 3.9+ runtime with `cryptography`, `pyOpenSSL` for client handshake scripts.
- Test certificates and CA infrastructure for validating hybrid TLS configurations.
- Env/config: see README for required secrets and endpoints.
