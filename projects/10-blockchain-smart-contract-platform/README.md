# Project 10: Blockchain Smart Contract Platform

## Overview
Implements a decentralized finance (DeFi) protocol with modular smart contracts, Hardhat tooling, and CI pipelines that enforce
linting, testing, and static analysis.

## Phase 2 Architecture Diagram

![Blockchain Smart Contract Platform – Phase 2](render locally to PNG; output is .gitignored)

- **Context**: Users interact through wallets and a backend API while CI/CD deploys audited contract bundles to an upgradeable
  proxy that fronts staking, governance, and treasury modules.
- **Decision**: Keep off-chain services, oracle/indexer integrations, and on-chain contracts in distinct trust zones so
  Chainlink data, governance proposals, and treasury operations are independently governed.
- **Consequences**: Timelocked governance guards upgrades and fund movements, while subgraph data powers read-model APIs
  without exposing private keys. Keep the [Mermaid source](assets/diagrams/architecture.mmd) synchronized with the exported PNG.

## Components
- Solidity contracts for staking, governance, and treasury management.
- Hardhat project configuration with TypeScript tests and deployment scripts.
- Integration with Chainlink price feeds and OpenZeppelin security libraries.

## Quick Start
```bash
npm install
npx hardhat compile
npx hardhat test
npx hardhat run scripts/deploy.ts --network goerli
```

## Security
- Slither static analysis in CI (`scripts/analyze.sh`).
- Time-locked governance actions for treasury safety.
- Upgradeable proxy pattern with transparent admin.
