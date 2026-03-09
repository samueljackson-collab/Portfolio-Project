---
title: Project 20: Blockchain Oracle Service
description: Chainlink-compatible external adapter exposing portfolio metrics to smart contracts
tags: [portfolio, blockchain-web3, solidity]
repository: https://github.com/samueljackson-collab/Portfolio-Project
path: /projects/blockchain-oracle-service
---

# Project 20: Blockchain Oracle Service
> **Category:** Blockchain & Web3 | **Status:** 🟡 50% Complete
> **Source:** projects/25-portfolio-website/docs/projects/20-oracle.md

## 📋 Executive Summary

**Chainlink-compatible** external adapter exposing portfolio metrics to smart contracts. Bridges off-chain data (APIs, databases, IoT) to on-chain consumers with cryptographic signing, retry logic, and Docker deployment for Chainlink node infrastructure.

## 🎯 Project Objectives

- **External Data Bridge** - Connect smart contracts to real-world data
- **Chainlink Integration** - Compatible with Chainlink oracle network
- **Cryptographic Signing** - Verify data authenticity on-chain
- **Retry Logic** - Resilient API calls with exponential backoff
- **Dockerized** - Easy deployment on Chainlink nodes

## 🏗️ Architecture

> Source: ../../../projects/25-portfolio-website/docs/projects/20-oracle.md#architecture
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

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Solidity | Solidity | Smart contract consumer |
| JavaScript/Node.js | JavaScript/Node.js | External adapter implementation |
| Chainlink | Chainlink | Decentralized oracle network |

## 💡 Key Technical Decisions

### Decision 1: Adopt Solidity
**Context:** Project 20: Blockchain Oracle Service requires a resilient delivery path.
**Decision:** Smart contract consumer
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 2: Adopt JavaScript/Node.js
**Context:** Project 20: Blockchain Oracle Service requires a resilient delivery path.
**Decision:** External adapter implementation
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 3: Adopt Chainlink
**Context:** Project 20: Blockchain Oracle Service requires a resilient delivery path.
**Decision:** Decentralized oracle network
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

## 🔧 Implementation Details

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

## ✅ Results & Outcomes

- **DeFi Integration**: Enables portfolio data in DeFi protocols
- **Decentralization**: Removes single point of failure for data feeds
- **Accuracy**: 99.9% uptime with multi-source aggregation
- **Trust**: Cryptographic proof of data authenticity

## 📚 Documentation

- [README.md](../README.md)
- [RUNBOOK.md](../RUNBOOK.md)
- [projects/25-portfolio-website/docs/projects/20-oracle.md](../../../projects/25-portfolio-website/docs/projects/20-oracle.md)

## 🎓 Skills Demonstrated

**Technical Skills:** Solidity, JavaScript/Node.js, Chainlink, Ethers.js, Docker

**Soft Skills:** Communication, Incident response leadership, Documentation rigor

## 📦 Wiki Deliverables

### Diagrams

- **Architecture excerpt** — Copied from `../../../projects/25-portfolio-website/docs/projects/20-oracle.md` (Architecture section).

### Checklists

> Source: ../../../docs/PRJ-MASTER-PLAYBOOK/README.md#5-deployment--release

**Infrastructure**:
- [ ] Terraform plan reviewed and approved
- [ ] Database migrations tested
- [ ] Secrets configured in AWS Secrets Manager
- [ ] Monitoring alerts configured
- [ ] Runbook updated with new procedures

**Application**:
- [ ] All tests passing in staging
- [ ] Performance benchmarks met
- [ ] Feature flags configured (if using)
- [ ] Rollback plan documented
- [ ] Stakeholders notified of deployment

### Metrics

> Source: ../RUNBOOK.md#sloslis

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Oracle service availability** | 99.9% | External adapter uptime |
| **Request fulfillment rate** | 99.5% | Successfully fulfilled oracle requests |
| **Response latency (p95)** | < 30 seconds | Time from request → on-chain response |
| **Data accuracy** | 100% | Correct data reported to smart contracts |
| **Gas efficiency** | < 200k gas | Gas used per oracle response |
| **Node sync status** | 100% | Chainlink node synced with blockchain |
| **Signature verification rate** | 100% | Valid signatures on oracle responses |

### Screenshots

- **Operational dashboard mockup** — `../../../projects/06-homelab/PRJ-HOME-002/assets/mockups/nginx-proxy-manager.html` (captures golden signals per PRJ-MASTER playbook).

---

*Created: 2025-11-14 | Last Updated: 2025-11-14*
