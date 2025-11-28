# Project 21: Quantum-Safe Cryptography

## Overview
Hybrid key exchange service that combines Kyber KEM with classical ECDH for defense-in-depth.

## Architecture
- **Context:** Clients establish sessions that require quantum-resistant confidentiality while remaining compatible with existing TLS stacks and audit requirements.
- **Decision:** Expose an API gateway that performs parallel Kyber and ECDH exchanges, combines secrets into a session key, and stores artifacts in a hardened KMS/PKI domain with audit trails.
- **Consequences:** Strengthens forward secrecy against quantum adversaries, but adds operational complexity around hybrid certificate management and key lifecycle.

[Mermaid source](assets/diagrams/architecture.mmd) · Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

## Usage
```bash
pip install -r requirements.txt
python src/key_exchange.py
```
