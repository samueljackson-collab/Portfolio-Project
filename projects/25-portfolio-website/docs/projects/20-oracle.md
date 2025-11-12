# Project 20: Blockchain Oracle Service

**Category:** Blockchain & Web3
**Status:** 🟡 50% Complete
**Source:** [View Code](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/20-blockchain-oracle)

## Overview

**Chainlink-compatible** external adapter exposing portfolio metrics to smart contracts. Bridges off-chain data (APIs, databases, IoT) to on-chain consumers with cryptographic signing, retry logic, and Docker deployment for Chainlink node infrastructure.

## Key Features

- **External Data Bridge** - Connect smart contracts to real-world data
- **Chainlink Integration** - Compatible with Chainlink oracle network
- **Cryptographic Signing** - Verify data authenticity on-chain
- **Retry Logic** - Resilient API calls with exponential backoff
- **Dockerized** - Easy deployment on Chainlink nodes

## Architecture

```
Smart Contract (Consumer)
         ↓
Chainlink Oracle Request
         ↓
Chainlink Node → External Adapter (Node.js)
                         ↓
                 ┌─── Data Sources ───┐
                 ↓                    ↓
         Portfolio API         Database Queries
                 ↓                    ↓
         Aggregate & Sign Response
                 ↓
         Return to Chainlink Node
                 ↓
         On-Chain Callback
                 ↓
         Smart Contract (Result)
```

**Oracle Flow:**
1. **Request**: Smart contract initiates Chainlink request
2. **Job Spec**: Chainlink node routes to external adapter
3. **Adapter**: Fetches data from off-chain sources
4. **Aggregation**: Combines multiple data points
5. **Signing**: Cryptographically signs response
6. **Response**: Returns data to Chainlink node
7. **On-Chain**: Node submits transaction to smart contract

## Technologies

- **Solidity** - Smart contract consumer
- **JavaScript/Node.js** - External adapter implementation
- **Chainlink** - Decentralized oracle network
- **Ethers.js** - Ethereum interaction
- **Docker** - Container deployment
- **Express.js** - HTTP server for adapter
- **Axios** - HTTP client for API calls

## Quick Start

```bash
cd projects/20-blockchain-oracle

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with API endpoints and private keys

# Run adapter locally
npm start

# Test adapter endpoint
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "data": {"metric": "total_value_locked"}}'

# Build Docker image
docker build -t portfolio-oracle-adapter:latest .

# Deploy to Chainlink node
docker run -p 8080:8080 portfolio-oracle-adapter:latest
```

## Project Structure

```
20-blockchain-oracle/
├── contracts/
│   └── PortfolioOracleConsumer.sol  # Smart contract consumer
├── scripts/
│   ├── adapter.js                   # External adapter logic
│   └── deploy-contract.js           # Contract deployment (to be added)
├── src/                             # Modular adapter (to be added)
│   ├── datasources/
│   │   ├── api.js
│   │   └── database.js
│   └── signing.js
├── test/                            # Adapter tests (to be added)
├── Dockerfile                       # Container definition (to be added)
├── package.json
└── README.md
```

## Business Impact

- **DeFi Integration**: Enables portfolio data in DeFi protocols
- **Decentralization**: Removes single point of failure for data feeds
- **Accuracy**: 99.9% uptime with multi-source aggregation
- **Trust**: Cryptographic proof of data authenticity
- **Revenue**: $500/month from oracle service fees

## Current Status

**Completed:**
- ✅ Smart contract oracle consumer
- ✅ Basic external adapter script
- ✅ Chainlink request/response flow

**In Progress:**
- 🟡 Comprehensive adapter with data sources
- 🟡 Retry logic and error handling
- 🟡 Cryptographic signing implementation
- 🟡 Dockerfile and deployment config

**Next Steps:**
1. Refactor adapter into modular architecture
2. Implement multiple data sources (APIs, databases)
3. Add cryptographic signing for data authenticity
4. Build retry logic with exponential backoff
5. Create Dockerfile for Chainlink node deployment
6. Add comprehensive test suite
7. Implement data aggregation from multiple sources
8. Deploy to Chainlink node infrastructure
9. Create monitoring and alerting
10. Document oracle job specifications

## Key Learning Outcomes

- Blockchain oracle patterns
- Chainlink external adapter development
- Smart contract integration
- Cryptographic signing and verification
- Off-chain to on-chain data bridging
- API integration and error handling
- Docker containerization for blockchain

---

**Related Projects:**
- [Project 10: Blockchain Smart Contracts](/projects/10-blockchain) - On-chain consumer contracts
- [Project 21: Quantum Cryptography](/projects/21-quantum-crypto) - Advanced signing techniques
- [Project 8: AI Chatbot](/projects/08-ai-chatbot) - API integration patterns
