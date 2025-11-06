# Project 20 · Blockchain Oracle Service

## 📌 Overview
Deliver a resilient blockchain oracle network that ingests off-chain market data, validates integrity, and publishes signed price feeds to smart contracts. The design prioritizes decentralization, tamper resistance, and auditable data pipelines.

## 🏗️ Architecture Highlights
- **Oracle nodes** deployed across multiple regions using Kubernetes with secure enclave signing (AWS Nitro Enclaves).
- **Data aggregation layer** pulling from premium APIs (Bloomberg, Kaiko) with medianization and anomaly detection.
- **Consensus mechanism** leveraging BFT-style committee signing and threshold signatures via Hashicorp Vault Transit.
- **On-chain adapters** implemented as Solidity smart contracts with fallback feeds and circuit breakers.
- **Monitoring & alerting** using Chainlink OCR metrics, Prometheus, and contract event watchers.

```
Off-chain APIs --> Ingestion Workers --> Validation & Aggregation --> Signing Committee --> On-chain Feed
```

## 🚀 Implementation Steps
1. **Provision validator nodes** with Terraform modules that deploy EKS clusters, configure Nitro Enclaves, and attach HSM-backed KMS keys.
2. **Implement data ingestion** microservices with retry/backoff, schema validation, and signed payload storage in DynamoDB.
3. **Run anomaly detection** using Prophet or Z-score models to reject outliers before aggregation.
4. **Coordinate signing** via Vault's Shamir key shares, requiring quorum approvals before publishing.
5. **Publish feeds on-chain** using Chainlink compatible jobs that push updates to Ethereum and Polygon contracts.
6. **Expose client SDK** for consuming price data with automatic fallback to secondary feeds if latency exceeds SLOs.
7. **Audit trail** by hashing payloads to IPFS and storing references in a compliance ledger (Qldb/Hyperledger Fabric).

## 🧩 Key Components
```typescript
// projects/20-blockchain-oracle-service/contracts/PriceFeed.sol
pragma solidity ^0.8.20;

contract PriceFeed {
    address public admin;
    uint256 public price;
    uint256 public lastUpdated;
    uint256 public heartbeat = 60; // seconds

    event PriceUpdated(uint256 newPrice, uint256 timestamp);

    modifier onlyAdmin() {
        require(msg.sender == admin, "not authorized");
        _;
    }

    constructor(address _admin) {
        admin = _admin;
    }

    function updatePrice(uint256 _price) external onlyAdmin {
        require(block.timestamp - lastUpdated < heartbeat * 2, "stale update");
        price = _price;
        lastUpdated = block.timestamp;
        emit PriceUpdated(_price, block.timestamp);
    }
}
```

## 🛡️ Fail-safes & Operations
- **Circuit breakers** disabling on-chain updates when deviation thresholds exceed configurable bounds.
- **Slashing & reputation** for oracle nodes using signed attestations and penalty deposits to discourage malicious behavior.
- **Disaster recovery** with rapid redeploy scripts and encrypted backups of key material stored in offline HSM vaults.
- **Compliance logging** feeding Splunk dashboards and automatic SOC2 evidence collection.
