# Web3 Simple Smart Contract

## Overview
A Solidity smart contract demonstrating secure tokenized task rewards on the Ethereum network. Includes Hardhat tooling, tests, and deployment scripts.

## Contract Highlights
- ERC-20 compliant token with capped supply for task completion rewards.
- Role-based access using OpenZeppelin AccessControl (admin, minter, pauser).
- Safe math operations and paused state to mitigate incidents.

## Development Workflow
1. Install dependencies: `npm install`.
2. Run local network: `npx hardhat node`.
3. Execute tests: `npx hardhat test` with coverage via `solidity-coverage`.
4. Deploy to testnet: `npx hardhat run scripts/deploy.ts --network sepolia`.
5. Verify contract on Etherscan: `npx hardhat verify`.

## Security Practices
- Uses Slither and MythX (optional) for static analysis.
- Follows best practices for upgradeability (UUPS pattern optional) documented in ADR.
- Private keys handled via `.env` with Vault-managed secrets in CI.

## Operations
- Scripts for token distribution, airdrops, and treasury management.
- Event indexing pipeline integrates with The Graph or serverless functions.
- Runbook covers incident response (pausing contract) and governance proposals.

