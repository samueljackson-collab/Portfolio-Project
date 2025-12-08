# Architecture

Stack: OpenSSL 3 + OQS provider, Docker, Python clients.

Data/Control flow: Build openssl image with OQS, run demo server, execute clients negotiating hybrid ciphers and validate latency/compat.

Dependencies:
- OpenSSL 3 + OQS provider, Docker, Python clients.
- Env/config: see README for required secrets and endpoints.
