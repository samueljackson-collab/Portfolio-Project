# Project 20: Blockchain Oracle Service

## Overview
Chainlink-compatible external adapter exposing portfolio metrics to smart contracts.

## Architecture
- **Context:** Smart contracts need signed, reliable portfolio metrics fetched from off-chain systems without trusting a single data source.
- **Decision:** Use a Chainlink node backed by an external adapter that aggregates and signs data, with retries and caching before publishing responses to consumer contracts.
- **Consequences:** Provides verifiable on-chain data delivery, but requires secure key custody on the oracle node and robust observability of adapter latency and failures.

[Mermaid source](assets/diagrams/architecture.mmd) · Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

## Components
- Solidity consumer contract for on-chain access.
- Node.js adapter that signs responses and handles retries.
- Dockerfile for rapid deployment on Chainlink node infrastructure.
