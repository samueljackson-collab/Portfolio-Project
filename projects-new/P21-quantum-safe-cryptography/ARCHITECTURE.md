# Architecture

Stack: OpenSSL 3 + OQS provider, Docker, Python clients.

Data/Control flow: Build openssl image with OQS, run demo server, execute clients negotiating hybrid ciphers and validate latency/compat.

Dependencies:
- OpenSSL 3.0+ with liboqs-openssl provider for post-quantum algorithms.
- Docker 20.10+ for containerized builds and runtime isolation.
- Python 3.8+ with `cryptography` library for client implementations.
- Sufficient entropy sources for key generation in production environments.
- Env/config: see README for required secrets and endpoints.
