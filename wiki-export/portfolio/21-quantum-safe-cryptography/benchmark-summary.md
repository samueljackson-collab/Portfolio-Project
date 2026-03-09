---
title: Benchmark Summary
description: Generated: 2026-01-22T15:33:47.643564Z - Hybrid PQC public key: 1184 bytes - Hybrid classical public key: 32 bytes - Hybrid PQC ciphertext: 64 bytes - Hybrid classical ephemeral public key: 32 bytes -
tags: [cryptography, documentation, portfolio, quantum-computing]
path: portfolio/21-quantum-safe-cryptography/benchmark-summary
created: 2026-03-08T22:19:13.287858+00:00
updated: 2026-03-08T22:04:38.633902+00:00
---

# Benchmark Summary

Generated: 2026-01-22T15:33:47.643564Z

## Protocol Payload Sizes

- Hybrid PQC public key: 1184 bytes
- Hybrid classical public key: 32 bytes
- Hybrid PQC ciphertext: 64 bytes
- Hybrid classical ephemeral public key: 32 bytes
- Signature public key: 32 bytes
- Signature bytes: 64 bytes

## Benchmark Averages

- Classical X25519 key exchange: 0.321 ms mean, 64 bytes payload
- PQC Kyber768-FALLBACK KEM: 0.295 ms mean, 1248 bytes payload
- Classical Ed25519 signature: 0.397 ms mean, 64 bytes payload
- PQC Dilithium3-FALLBACK signature: 1.033 ms mean, 64 bytes payload
