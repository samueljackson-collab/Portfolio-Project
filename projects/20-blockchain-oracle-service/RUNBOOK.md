# Runbook — Project 20 (Blockchain Oracle Service)

## Overview

Production operations runbook for the Blockchain Oracle Service, a Chainlink-compatible external adapter that exposes portfolio metrics to smart contracts on-chain with cryptographic signing and retry mechanisms.

**System Components:**
- Chainlink node infrastructure
- External adapter (Node.js service)
- Solidity consumer smart contracts
- Oracle job specifications
- Cryptographic signing service (ECDSA)
- Off-chain data aggregation layer
- Request/response queue with retries
- Blockchain network connections (Ethereum, Polygon, etc.)

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Oracle service availability** | 99.9% | External adapter uptime |
| **Request fulfillment rate** | 99.5% | Successfully fulfilled oracle requests |
| **Response latency (p95)** | < 30 seconds | Time from request → on-chain response |
| **Data accuracy** | 100% | Correct data reported to smart contracts |
| **Gas efficiency** | < 200k gas | Gas used per oracle response |
| **Node sync status** | 100% | Chainlink node synced with blockchain |
| **Signature verification rate** | 100% | Valid signatures on oracle responses |

---

## Dashboards & Alerts

### Dashboards

#### Oracle Service Health Dashboard
```bash
# Check external adapter status
kubectl get pods -n oracle -l app=external-adapter

# Check adapter health endpoint
kubectl port-forward -n oracle svc/external-adapter 8080:8080 &
curl -s http://localhost:8080/health

# Check adapter logs
kubectl logs -n oracle -l app=external-adapter --tail=100

# Check adapter metrics
curl -s http://localhost:8080/metrics | grep -E "(oracle|adapter|request)"
```

#### Chainlink Node Dashboard
```bash
# Access Chainlink node UI
kubectl port-forward -n oracle svc/chainlink-node 6688:6688
# Open http://localhost:6688 in browser

# Check node status via CLI
kubectl exec -n oracle deploy/chainlink-node -- chainlink admin status

# Check node balance
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink keys eth list

# Check job runs
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink jobs list
```

#### On-Chain Activity Dashboard
```bash
# Check oracle contract address
kubectl get configmap oracle-config -n oracle -o jsonpath='{.data.ORACLE_CONTRACT_ADDRESS}'

# Monitor on-chain events (using web3)
node <<EOF
const Web3 = require('web3');
const web3 = new Web3(process.env.RPC_URL);
const oracleAddress = process.env.ORACLE_CONTRACT_ADDRESS;

// Check oracle contract balance
web3.eth.getBalance(oracleAddress).then(balance => {
  console.log('Oracle balance:', web3.utils.fromWei(balance, 'ether'), 'ETH');
});

// Check recent fulfillments
const oracleABI = [...];  // Load ABI
const oracle = new web3.eth.Contract(oracleABI, oracleAddress);
oracle.getPastEvents('OracleRequest', {
  fromBlock: 'latest',
  toBlock: 'latest'
}).then(events => {
  console.log('Recent requests:', events.length);
});
EOF
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Oracle service down | Immediate | Restart service, check connectivity |
| **P0** | Node out of gas (< 0.1 ETH) | Immediate | Fund oracle wallet |
| **P0** | Request fulfillment failure > 5% | Immediate | Check data source, validate signatures |
| **P1** | High response latency (> 60s) | 15 minutes | Investigate bottleneck, scale adapter |
| **P1** | Node not synced with blockchain | 15 minutes | Restart node, check RPC connection |
| **P2** | Signature verification failures | 30 minutes | Check private key, verify signing service |
| **P2** | High gas prices (> 100 gwei) | 1 hour | Adjust gas price strategy |

#### Alert Queries (Prometheus)

```promql
# Oracle service down
up{job="external-adapter"} == 0

# High failure rate
(
  rate(oracle_requests_failed_total[5m])
  /
  rate(oracle_requests_total[5m])
) > 0.05

# High response latency
histogram_quantile(0.95,
  rate(oracle_response_duration_seconds_bucket[5m])
) > 30

# Low node balance
oracle_node_balance_eth < 0.1

# Node not synced
oracle_node_block_height < oracle_chain_block_height - 10

# Signature failures
rate(oracle_signature_failures_total[5m]) > 0
```

---

## Standard Operations

### Oracle Service Management

#### Deploy Oracle Service
```bash
# Create namespace
kubectl create namespace oracle

# Deploy PostgreSQL for Chainlink node
kubectl apply -f manifests/postgres.yaml

# Deploy Chainlink node
kubectl apply -f manifests/chainlink-node.yaml

# Deploy external adapter
kubectl apply -f manifests/external-adapter.yaml

# Verify deployments
kubectl get pods -n oracle
kubectl wait --for=condition=Ready pods -l app=chainlink-node -n oracle --timeout=300s
kubectl wait --for=condition=Ready pods -l app=external-adapter -n oracle --timeout=120s

# Check logs
kubectl logs -n oracle -l app=chainlink-node --tail=50
kubectl logs -n oracle -l app=external-adapter --tail=50
```

#### Configure Oracle Jobs
```bash
# Access Chainlink node
kubectl port-forward -n oracle svc/chainlink-node 6688:6688

# Log in to Chainlink UI
# http://localhost:6688
# Credentials from secret: kubectl get secret chainlink-credentials -n oracle

# Create job via CLI
kubectl exec -n oracle deploy/chainlink-node -- chainlink jobs create <<EOF
{
  "name": "Portfolio Metrics Oracle",
  "type": "directrequest",
  "schemaVersion": 1,
  "externalJobID": "$(uuidgen)",
  "evmChainID": "1",
  "contractAddress": "$ORACLE_CONTRACT_ADDRESS",
  "minContractPayment": "0",
  "observationSource": """
    decode_log   [type=ethabidecodelog
                  abi="OracleRequest(bytes32 indexed specId, address requester, bytes32 requestId, uint256 payment, address callbackAddr, bytes4 callbackFunctionId, uint256 cancelExpiration, uint256 dataVersion, bytes data)"]

    decode_cbor  [type=cborparse data="$(decode_log.data)"]
    fetch        [type=bridge name="external-adapter" requestData="{\\"id\\": $(jobSpec.externalJobID), \\\"data\\": { \\\"metric\\": $(decode_cbor.metric)}}"]
    parse        [type=jsonparse path="data,result"]
    encode_data  [type=ethabiencode abi="(bytes32 requestId, uint256 result)" data="{ \\\"requestId\\": $(decode_log.requestId), \\\"result\\": $(parse) }"]
    encode_tx    [type=ethabiencode
                  abi="fulfillOracleRequest(bytes32 requestId, uint256 payment, address callbackAddress, bytes4 callbackFunctionId, uint256 expiration, bytes32 data)"
                  data="{\\"requestId\\": $(decode_log.requestId), \\\"payment\\": $(decode_log.payment), \\\"callbackAddress\\": $(decode_log.callbackAddr), \\\"callbackFunctionId\\": $(decode_log.callbackFunctionId), \\\"expiration\\": $(decode_log.cancelExpiration), \\\"data\\": $(encode_data)}"]
    submit_tx    [type=ethtx to="$ORACLE_CONTRACT_ADDRESS" data="$(encode_tx)"]

    decode_log -> decode_cbor -> fetch -> parse -> encode_data -> encode_tx -> submit_tx
  """
}
EOF

# Verify job is active
kubectl exec -n oracle deploy/chainlink-node -- chainlink jobs list
```

#### Fund Oracle Wallet
```bash
# Get oracle wallet address
ORACLE_ADDRESS=$(kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink keys eth list | jq -r '.[0].address')

echo "Oracle address: $ORACLE_ADDRESS"

# Check current balance
kubectl exec -n oracle deploy/chainlink-node -- chainlink admin balance

# Fund wallet (from external wallet)
# Use MetaMask, hardware wallet, or CLI tool to send ETH

# Verify balance
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink keys eth list | jq '.[0].ethBalance'
```

### External Adapter Operations

#### Update Adapter Configuration
```bash
# Update data source endpoints
kubectl edit configmap external-adapter-config -n oracle

# Reload adapter
kubectl rollout restart deployment/external-adapter -n oracle

# Verify configuration
kubectl logs -n oracle -l app=external-adapter --tail=50 | grep "Config loaded"
```

#### Test Adapter Endpoint
```bash
# Port-forward adapter
kubectl port-forward -n oracle svc/external-adapter 8080:8080 &

# Test health endpoint
curl http://localhost:8080/health

# Test adapter request
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-request-1",
    "data": {
      "metric": "total_value"
    }
  }'

# Expected response:
# {
#   "jobRunID": "test-request-1",
#   "data": {
#     "result": 1234567
#   },
#   "statusCode": 200
# }
```

#### Monitor Adapter Performance
```bash
# Check request rate
kubectl port-forward -n oracle svc/external-adapter 8080:8080 &
curl -s http://localhost:8080/metrics | grep oracle_requests_total

# Check response times
curl -s http://localhost:8080/metrics | grep oracle_response_duration_seconds

# Check error rate
curl -s http://localhost:8080/metrics | grep oracle_requests_failed_total

# View recent logs
kubectl logs -n oracle -l app=external-adapter --tail=100 -f
```

### Smart Contract Operations

#### Deploy Oracle Consumer Contract
```javascript
// deploy-consumer.js
const { ethers } = require('hardhat');

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log('Deploying contracts with:', deployer.address);

  // Deploy consumer contract
  const Consumer = await ethers.getContractFactory('PortfolioMetricsConsumer');
  const consumer = await Consumer.deploy(
    process.env.ORACLE_CONTRACT_ADDRESS,  // Oracle address
    process.env.JOB_ID,                   // Job ID
    ethers.utils.parseEther('0.1')       // LINK payment
  );

  await consumer.deployed();
  console.log('Consumer deployed to:', consumer.address);

  // Fund consumer with LINK
  const linkToken = await ethers.getContractAt('IERC20', process.env.LINK_TOKEN_ADDRESS);
  await linkToken.transfer(consumer.address, ethers.utils.parseEther('10'));
  console.log('Consumer funded with 10 LINK');
}

main()
  .then(() => process.exit(0))
  .catch(error => {
    console.error(error);
    process.exit(1);
  });
```

```bash
# Deploy consumer contract
npx hardhat run scripts/deploy-consumer.js --network mainnet

# Verify contract on Etherscan
npx hardhat verify --network mainnet <contract-address> \
  <oracle-address> <job-id> <link-payment>
```

#### Request Portfolio Metrics
```javascript
// request-metrics.js
const { ethers } = require('hardhat');

async function main() {
  const consumer = await ethers.getContractAt(
    'PortfolioMetricsConsumer',
    process.env.CONSUMER_CONTRACT_ADDRESS
  );

  // Request total portfolio value
  const tx = await consumer.requestTotalValue();
  console.log('Request transaction:', tx.hash);

  // Wait for confirmation
  await tx.wait();
  console.log('Request confirmed');

  // Wait for fulfillment (poll contract)
  console.log('Waiting for oracle response...');
  let result;
  for (let i = 0; i < 30; i++) {
    result = await consumer.totalValue();
    if (result.gt(0)) {
      console.log('Result received:', ethers.utils.formatUnits(result, 0));
      break;
    }
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
}

main()
  .then(() => process.exit(0))
  .catch(error => {
    console.error(error);
    process.exit(1);
  });
```

```bash
# Run request script
npx hardhat run scripts/request-metrics.js --network mainnet
```

---

## Incident Response

### P0: Oracle Service Down

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check service status
kubectl get pods -n oracle -l app=external-adapter

# 2. Check logs for errors
kubectl logs -n oracle -l app=external-adapter --tail=100

# 3. Check recent events
kubectl get events -n oracle --sort-by='.lastTimestamp' | head -20

# 4. Restart service
kubectl rollout restart deployment/external-adapter -n oracle

# 5. Verify recovery
kubectl wait --for=condition=Ready pods -l app=external-adapter -n oracle --timeout=120s
curl http://localhost:8080/health
```

**Investigation (5-20 minutes):**
```bash
# Check resource usage
kubectl top pods -n oracle -l app=external-adapter

# Check for OOMKilled
kubectl describe pod -n oracle -l app=external-adapter | grep -A 10 "State:"

# Check database connectivity
kubectl exec -n oracle deploy/external-adapter -- \
  node -e "const pg = require('pg'); const client = new pg.Client(process.env.DATABASE_URL); client.connect().then(() => console.log('DB OK')).catch(err => console.error(err));"

# Check RPC connectivity
kubectl exec -n oracle deploy/external-adapter -- \
  curl -X POST $RPC_URL \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

**Recovery:**
```bash
# If configuration issue, restore from backup
kubectl apply -f backup/external-adapter-config.yaml

# If resource exhaustion, scale up
kubectl scale deployment/external-adapter -n oracle --replicas=3

# Verify service is handling requests
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"id": "test", "data": {"metric": "total_value"}}'
```

### P0: Node Out of Gas

**Immediate Actions:**
```bash
# 1. Check node balance
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink keys eth list | jq '.[0].ethBalance'

# 2. Get oracle address
ORACLE_ADDRESS=$(kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink keys eth list | jq -r '.[0].address')

# 3. Fund oracle wallet immediately
# Use hot wallet or exchange to send ETH
# Recommended: 1-5 ETH depending on gas prices and request volume

# 4. Verify balance updated
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink admin balance

# 5. Check pending requests
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink jobs runs list --limit 10
```

**Prevention:**
```bash
# Set up balance monitoring
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: balance-monitor
  namespace: oracle
data:
  monitor.sh: |
    #!/bin/bash
    BALANCE=\$(chainlink keys eth list | jq -r '.[0].ethBalance')
    THRESHOLD="0.5"
    if (( \$(echo "\$BALANCE < \$THRESHOLD" | bc -l) )); then
      echo "ALERT: Oracle balance low: \$BALANCE ETH"
      # Send alert to monitoring system
      curl -X POST \$ALERT_WEBHOOK_URL -d "{\"text\":\"Oracle balance low: \$BALANCE ETH\"}"
    fi
EOF

# Run as CronJob
kubectl create cronjob balance-monitor -n oracle \
  --image=chainlink/chainlink:latest \
  --schedule="*/15 * * * *" \
  -- /bin/bash /scripts/monitor.sh
```

### P0: Request Fulfillment Failure

**Investigation:**
```bash
# 1. Check recent job runs
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink jobs runs list --limit 20

# 2. Check failed runs
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink jobs runs list --status errored

# 3. Check adapter logs
kubectl logs -n oracle -l app=external-adapter --tail=200 | grep -i error

# 4. Check on-chain events
node <<EOF
const Web3 = require('web3');
const web3 = new Web3(process.env.RPC_URL);
const oracleABI = [...];  // Load ABI
const oracle = new web3.eth.Contract(oracleABI, process.env.ORACLE_CONTRACT_ADDRESS);

oracle.getPastEvents('OracleRequest', {
  fromBlock: 'latest',
  toBlock: 'latest'
}).then(events => {
  console.log('Recent requests:', events);
});
EOF
```

**Common Causes & Fixes:**

**Data Source Unavailable:**
```bash
# Test data source
kubectl exec -n oracle deploy/external-adapter -- \
  curl -v $DATA_SOURCE_URL

# Use fallback data source
kubectl set env deployment/external-adapter -n oracle \
  DATA_SOURCE_URL=$FALLBACK_DATA_SOURCE_URL

# Restart adapter
kubectl rollout restart deployment/external-adapter -n oracle
```

**Signature Verification Failure:**
```bash
# Check private key is set
kubectl get secret oracle-private-key -n oracle -o jsonpath='{.data.PRIVATE_KEY}' | base64 -d

# Verify signing service
kubectl logs -n oracle -l app=external-adapter | grep -i "sign\|signature"

# Test signature generation
kubectl exec -n oracle deploy/external-adapter -- node <<EOF
const ethers = require('ethers');
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY);
const message = 'test message';
const signature = wallet.signMessage(message);
console.log('Signature:', signature);
EOF
```

**Transaction Reverted:**
```bash
# Check gas price settings
kubectl get configmap external-adapter-config -n oracle -o jsonpath='{.data.GAS_PRICE_STRATEGY}'

# Increase gas limit
kubectl patch configmap external-adapter-config -n oracle --type merge -p '{"data":{"GAS_LIMIT":"300000"}}'

# Check transaction logs
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink txs list --limit 10
```

### P1: High Response Latency

**Investigation:**
```bash
# 1. Check adapter metrics
kubectl port-forward -n oracle svc/external-adapter 8080:8080 &
curl -s http://localhost:8080/metrics | grep oracle_response_duration_seconds

# 2. Check data source latency
time curl -X GET $DATA_SOURCE_URL

# 3. Check blockchain RPC latency
time curl -X POST $RPC_URL \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

# 4. Check node processing time
kubectl logs -n oracle -l app=chainlink-node --tail=100 | grep "duration\|elapsed"
```

**Mitigation:**
```bash
# Scale up adapter
kubectl scale deployment/external-adapter -n oracle --replicas=5

# Add caching layer
kubectl apply -f manifests/redis-cache.yaml

# Update adapter to use cache
kubectl set env deployment/external-adapter -n oracle \
  REDIS_URL=redis://redis.oracle.svc.cluster.local:6379

# Switch to faster RPC provider
kubectl set env deployment/chainlink-node -n oracle \
  ETH_URL=$FAST_RPC_URL
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: "Insufficient LINK balance"

**Symptoms:**
```
Error: Request failed - Insufficient LINK
Transaction reverted: Not enough LINK
```

**Diagnosis:**
```bash
# Check consumer contract LINK balance
node <<EOF
const { ethers } = require('hardhat');
const linkToken = await ethers.getContractAt('IERC20', process.env.LINK_TOKEN_ADDRESS);
const balance = await linkToken.balanceOf(process.env.CONSUMER_CONTRACT_ADDRESS);
console.log('LINK balance:', ethers.utils.formatEther(balance));
EOF
```

**Solution:**
```bash
# Transfer LINK to consumer contract
node <<EOF
const { ethers } = require('hardhat');
const [signer] = await ethers.getSigners();
const linkToken = await ethers.getContractAt('IERC20', process.env.LINK_TOKEN_ADDRESS);
const tx = await linkToken.transfer(
  process.env.CONSUMER_CONTRACT_ADDRESS,
  ethers.utils.parseEther('10')
);
await tx.wait();
console.log('Transferred 10 LINK to consumer');
EOF
```

---

#### Issue: "Node not synced with blockchain"

**Symptoms:**
```
Node block height: 12345678
Chain block height: 12345900
Lag: 222 blocks
```

**Diagnosis:**
```bash
# Check node sync status
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink admin status | grep "Current Block"

# Check RPC endpoint
curl -X POST $RPC_URL \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_syncing","params":[],"id":1}'
```

**Solution:**
```bash
# Restart node
kubectl rollout restart deployment/chainlink-node -n oracle

# Switch to different RPC endpoint
kubectl set env deployment/chainlink-node -n oracle \
  ETH_URL=$ALTERNATIVE_RPC_URL

# Check sync status
kubectl logs -n oracle -l app=chainlink-node -f | grep "sync"
```

---

#### Issue: "Oracle contract not responding"

**Symptoms:**
```
OracleRequest event not detected
No job runs triggered
```

**Diagnosis:**
```bash
# Check contract address is correct
kubectl get configmap oracle-config -n oracle -o jsonpath='{.data.ORACLE_CONTRACT_ADDRESS}'

# Check job configuration
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink jobs show <job-id>

# Check event logs
node <<EOF
const Web3 = require('web3');
const web3 = new Web3(process.env.RPC_URL);
const oracleABI = [...];
const oracle = new web3.eth.Contract(oracleABI, process.env.ORACLE_CONTRACT_ADDRESS);
oracle.getPastEvents('allEvents', {fromBlock: 'latest', toBlock: 'latest'})
  .then(events => console.log('Events:', events));
EOF
```

**Solution:**
```bash
# Update job contract address
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink jobs delete <job-id>

# Recreate job with correct address
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink jobs create < job-spec.json

# Verify job is active
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink jobs list
```

---

## Maintenance Procedures

### Daily Tasks

```bash
# Morning health check
# 1. Check oracle service status
kubectl get pods -n oracle

# 2. Check node balance
kubectl exec -n oracle deploy/chainlink-node -- chainlink admin balance

# 3. Check recent job runs
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink jobs runs list --limit 10

# 4. Check adapter health
curl http://localhost:8080/health

# 5. Check on-chain activity
node scripts/check-recent-requests.js
```

### Weekly Tasks

```bash
# 1. Review oracle performance
kubectl port-forward -n oracle svc/external-adapter 8080:8080 &
curl -s http://localhost:8080/metrics > metrics-$(date +%Y%m%d).txt

# 2. Review gas usage
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink txs list --limit 100 > transactions-$(date +%Y%m%d).txt

# 3. Backup configurations
kubectl get configmap,secret -n oracle -o yaml > backup/oracle-config-$(date +%Y%m%d).yaml

# 4. Update adapter dependencies
cd external-adapter/
npm audit
npm update
docker build -t external-adapter:latest .
kubectl set image deployment/external-adapter -n oracle external-adapter=external-adapter:latest

# 5. Review and optimize job specifications
kubectl exec -n oracle deploy/chainlink-node -- chainlink jobs list
# Review each job for optimization opportunities
```

### Monthly Tasks

```bash
# 1. Update Chainlink node version
kubectl set image deployment/chainlink-node -n oracle \
  chainlink-node=chainlink/chainlink:2.0.0

# 2. Review and optimize gas strategy
# Analyze historical gas usage
# Adjust gas price multipliers

# 3. Conduct disaster recovery drill
# Simulate oracle failure
# Test recovery procedures
# Verify backup wallets

# 4. Security audit
# Review private key security
# Check for unauthorized access
# Update credentials if needed

# 5. Capacity planning
# Review request volume trends
# Plan for scaling
# Optimize resource allocation
```

### Disaster Recovery

**Backup Strategy:**
```bash
# 1. Backup private keys (ENCRYPTED!)
kubectl get secret oracle-private-key -n oracle -o yaml > backup/private-key-encrypted.yaml

# 2. Backup node database
kubectl exec -n oracle deploy/postgres -- \
  pg_dump -U chainlink chainlink_db > backup/chainlink-db-$(date +%Y%m%d).sql

# 3. Backup configurations
kubectl get configmap,secret,deployment,service -n oracle -o yaml > backup/oracle-manifests.yaml

# 4. Backup job specifications
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink jobs list -o json > backup/jobs-$(date +%Y%m%d).json

# 5. Document oracle addresses
kubectl exec -n oracle deploy/chainlink-node -- \
  chainlink keys eth list > backup/oracle-addresses.txt
```

**Recovery Procedures:**
```bash
# 1. Restore namespace
kubectl create namespace oracle

# 2. Restore secrets (private keys)
kubectl apply -f backup/private-key-encrypted.yaml

# 3. Restore database
kubectl apply -f backup/postgres-deployment.yaml
kubectl wait --for=condition=Ready pods -l app=postgres -n oracle --timeout=120s
kubectl exec -n oracle deploy/postgres -- psql -U chainlink chainlink_db < backup/chainlink-db-latest.sql

# 4. Restore Chainlink node
kubectl apply -f backup/oracle-manifests.yaml
kubectl wait --for=condition=Ready pods -l app=chainlink-node -n oracle --timeout=300s

# 5. Restore jobs
for job in $(cat backup/jobs-latest.json | jq -c '.[]'); do
  echo "$job" | kubectl exec -i -n oracle deploy/chainlink-node -- chainlink jobs create
done

# 6. Verify functionality
kubectl exec -n oracle deploy/chainlink-node -- chainlink jobs list
curl http://localhost:8080/health
```

---

## Quick Reference

### Common Commands

```bash
# Check oracle status
kubectl get pods -n oracle
kubectl logs -n oracle -l app=external-adapter -f

# Check node balance
kubectl exec -n oracle deploy/chainlink-node -- chainlink admin balance

# List jobs
kubectl exec -n oracle deploy/chainlink-node -- chainlink jobs list

# Test adapter
curl -X POST http://localhost:8080 -H "Content-Type: application/json" -d '{"id":"test","data":{"metric":"total_value"}}'
```

### Emergency Response

```bash
# P0: Oracle service down
kubectl rollout restart deployment/external-adapter -n oracle

# P0: Out of gas
# Fund oracle wallet immediately with ETH

# P0: Fulfillment failures
kubectl logs -n oracle -l app=external-adapter --tail=200 | grep ERROR
kubectl logs -n oracle -l app=chainlink-node --tail=200 | grep ERROR

# P1: High latency
kubectl scale deployment/external-adapter -n oracle --replicas=5
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Blockchain/Oracle Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Submit PR with updates
