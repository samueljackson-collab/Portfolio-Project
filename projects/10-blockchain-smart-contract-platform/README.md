# Project 10: Blockchain Smart Contract Platform

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


## 📊 Portfolio Status Board

🟢 Done · 🟠 In Progress · 🔵 Planned

**Current Status:** 🟢 Done (Implemented)


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


## Code Generation Prompts

This section contains AI-assisted code generation prompts that can help you recreate or extend project components. These prompts are designed to work with AI coding assistants like Claude, GPT-4, or GitHub Copilot.

### Smart Contract Development

#### 1. Smart Contract
```
Create a Solidity smart contract for an ERC-20 token with minting, burning, and transfer restrictions, including comprehensive access controls
```

#### 2. Contract Tests
```
Generate Hardhat tests for smart contract functions covering normal operations, edge cases, access control, and gas optimization verification
```

#### 3. Deployment Script
```
Write a deployment script that deploys smart contracts to multiple networks (local, testnet, mainnet), verifies contracts on Etherscan, and configures initial parameters
```

### How to Use These Prompts

1. **Copy the prompt** from the code block above
2. **Customize placeholders** (replace [bracketed items] with your specific requirements)
3. **Provide context** to your AI assistant about:
   - Your development environment and tech stack
   - Existing code patterns and conventions in this project
   - Any constraints or requirements specific to your use case
4. **Review and adapt** the generated code before using it
5. **Test thoroughly** and adjust as needed for your specific scenario

### Best Practices

- Always review AI-generated code for security vulnerabilities
- Ensure generated code follows your project's coding standards
- Add appropriate error handling and logging
- Write tests for AI-generated components
- Document any assumptions or limitations
- Keep sensitive information (credentials, keys) in environment variables
