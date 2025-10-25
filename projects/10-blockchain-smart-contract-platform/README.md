# Project 10: Blockchain Smart Contract Platform

## Overview
Implements a decentralized finance (DeFi) protocol with modular smart contracts, Hardhat tooling, and CI pipelines that enforce linting, testing, and static analysis.

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
