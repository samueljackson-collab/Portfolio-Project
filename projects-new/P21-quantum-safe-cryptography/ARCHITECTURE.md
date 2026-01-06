# Architecture

Stack: OpenSSL 3 + OQS provider, Docker, Python clients.

Data/Control flow: Build openssl image with OQS, run demo server, execute clients negotiating hybrid ciphers and validate latency/compat.

Dependencies:
- OpenSSL 3.x runtime with OQS provider integration for post-quantum cryptography algorithms.
- Docker runtime environment for containerized OpenSSL builds and test servers.
- Python 3.8+ with cryptography libraries for client implementations and testing.
- Support for hybrid key exchange mechanisms (classical + post-quantum KEMs).
- Env/config: see README for required secrets and endpoints.
