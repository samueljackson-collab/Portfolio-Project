# Threat Model

Threats:
- Fallback to classical-only cipher
- Implementation bugs leaking keys
- Incompatible client libraries

Mitigations:
- Enforce cipher suites in config
- Use valgrind/asan in CI builds
- Matrix tests across clients
