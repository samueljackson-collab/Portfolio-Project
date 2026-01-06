# Architecture

Stack: OpenSSL 3 + OQS provider, Docker, Python clients.

Data/Control flow: Build openssl image with OQS, run demo server, execute clients negotiating hybrid ciphers and validate latency/compat.

Dependencies:
- OpenSSL 3.0+ with OQS provider (liboqs integration for post-quantum algorithms).
- Docker runtime for containerized TLS server and client test environments.
- Python 3.8+ with `cryptography`, `pytest` libraries for handshake validation.
- X.509 test certificates supporting hybrid key exchange algorithms.
- Env/config: see README for required secrets and endpoints.
