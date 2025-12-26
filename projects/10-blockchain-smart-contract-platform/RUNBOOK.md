# Runbook — Project 10 (Blockchain Smart Contract Platform)

## Overview

Production operations runbook for the Blockchain Smart Contract Platform (DeFi Protocol). This runbook covers smart contract deployment, monitoring, security operations, incident response, and troubleshooting for Solidity contracts on Ethereum-compatible networks.

**System Components:**
- Solidity Smart Contracts (staking, governance, treasury)
- Hardhat Development Environment
- Ethereum Mainnet / Layer 2 Networks
- Etherscan API (contract verification, monitoring)
- Chainlink Price Feeds (oracle integration)
- OpenZeppelin Security Libraries
- Slither Static Analyzer
- CI/CD Pipeline (GitHub Actions)
- Multi-sig Wallet (Gnosis Safe)
- Contract Monitoring Service

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Contract uptime** | 99.99% | Time contracts are operational and accessible |
| **Transaction success rate** | 99.5% | Successful on-chain transactions |
| **Gas optimization** | < 500k gas | Average gas per transaction |
| **Security audit coverage** | 100% | All contracts audited before mainnet |
| **Oracle data freshness** | < 5 minutes | Chainlink price feed update interval |
| **Multi-sig approval time** | < 2 hours | Time for governance actions approval |
| **Contract verification** | 100% | All contracts verified on Etherscan |

---

## Dashboards & Alerts

### Dashboards

#### Contract Status Dashboard
```bash
# Check contract deployment status
npx hardhat run scripts/check_contracts.js --network mainnet

# Expected output:
# StakingContract: 0x123... (verified ✓)
# GovernanceContract: 0x456... (verified ✓)
# TreasuryContract: 0x789... (verified ✓)
# All contracts operational

# View on Etherscan
echo "StakingContract: https://etherscan.io/address/0x123..."
```

#### Transaction Monitoring
```bash
# Monitor recent transactions
npx hardhat run scripts/monitor_txs.js --network mainnet

# Check gas usage
curl "https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=$ETHERSCAN_API_KEY"

# View transaction history
curl "https://api.etherscan.io/api?module=account&action=txlist&address=0x123...&apikey=$ETHERSCAN_API_KEY"
```

#### Treasury Dashboard
```bash
# Check treasury balance
npx hardhat run scripts/check_treasury.js --network mainnet

# Expected output:
# Treasury Balance: 1000.5 ETH
# Pending Proposals: 2
# Active Timelock: 1

# View multi-sig wallet
echo "Gnosis Safe: https://app.safe.global/eth:0x789..."
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Contract exploited/drained | Immediate | Pause contract, emergency response |
| **P0** | Oracle data stale > 1 hour | Immediate | Switch to backup oracle, investigate |
| **P1** | Failed transactions > 10% | 15 minutes | Investigate, check gas prices |
| **P1** | Unusual treasury withdrawal | 15 minutes | Verify legitimacy, pause if suspicious |
| **P2** | High gas prices (> 200 gwei) | 30 minutes | Notify users, delay non-urgent txs |
| **P2** | Contract event anomaly | 30 minutes | Investigate event logs |
| **P3** | Etherscan verification pending | 1 hour | Retry verification |

#### Alert Queries

```bash
# Check for suspicious activity
npx hardhat run scripts/check_security.js --network mainnet

# Monitor treasury
TREASURY_BALANCE=$(cast balance 0x789... --rpc-url $RPC_URL)
if [ "$TREASURY_BALANCE" -lt "$THRESHOLD" ]; then
  echo "ALERT: Treasury balance below threshold"
fi

# Check oracle freshness
LAST_UPDATE=$(cast call $CHAINLINK_FEED "latestTimestamp()" --rpc-url $RPC_URL)
CURRENT_TIME=$(date +%s)
AGE=$((CURRENT_TIME - LAST_UPDATE))
if [ $AGE -gt 3600 ]; then
  echo "ALERT: Oracle data stale (${AGE}s old)"
fi
```

---

## Standard Operations

### Smart Contract Development & Testing

#### Development Workflow
```bash
# 1. Set up environment
npm install

# 2. Compile contracts
npx hardhat compile

# 3. Run tests
npx hardhat test

# Expected output:
#   StakingContract
#     ✓ should allow staking (123ms)
#     ✓ should calculate rewards correctly (89ms)
#     ✓ should allow unstaking after period (145ms)
#   24 passing (2s)

# 4. Check test coverage
npx hardhat coverage

# Target: > 95% coverage

# 5. Run static analysis
npm run analyze

# Or manually:
slither . --exclude-dependencies
```

#### Security Checks
```bash
# Run Slither static analyzer
slither contracts/ --exclude-dependencies --filter-paths node_modules

# Check for common vulnerabilities
slither contracts/ --detect reentrancy-eth,reentrancy-no-eth,reentrancy-benign

# Run Mythril (if installed)
myth analyze contracts/StakingContract.sol --solc-json mythril_config.json

# Check for known vulnerabilities
npm audit

# Review dependencies
npm ls --depth=0
```

### Deployment Operations

#### Deploy to Testnet
```bash
# 1. Set up environment variables
export PRIVATE_KEY="0x..."
export GOERLI_RPC_URL="https://goerli.infura.io/v3/..."
export ETHERSCAN_API_KEY="..."

# 2. Compile contracts
npx hardhat compile

# 3. Run deployment script
npx hardhat run scripts/deploy.ts --network goerli

# Expected output:
# Deploying contracts to Goerli...
# StakingContract deployed to: 0x123...
# GovernanceContract deployed to: 0x456...
# TreasuryContract deployed to: 0x789...
# Transaction hash: 0xabc...

# 4. Verify contracts
npx hardhat verify --network goerli 0x123... "arg1" "arg2"

# 5. Test on testnet
npx hardhat run scripts/test_deployed.ts --network goerli
```

#### Deploy to Mainnet
```bash
# ⚠️ CRITICAL: Use multi-sig for mainnet deployments

# 1. Pre-deployment checklist
cat > deployment_checklist.md << 'EOF'
# Mainnet Deployment Checklist

- [ ] All tests passing (100%)
- [ ] Test coverage > 95%
- [ ] Slither analysis clean
- [ ] External audit completed
- [ ] Multi-sig wallet configured
- [ ] Gas price acceptable (< 50 gwei)
- [ ] Backup plan documented
- [ ] Emergency pause mechanism tested
- [ ] Team available for monitoring
- [ ] Communication plan ready

EOF

# 2. Simulate deployment (fork)
npx hardhat node --fork https://mainnet.infura.io/v3/...
npx hardhat run scripts/deploy.ts --network localhost

# 3. Calculate gas costs
npx hardhat run scripts/estimate_gas.js --network mainnet

# 4. Deploy via multi-sig (Gnosis Safe)
# Create deployment transaction
npx hardhat run scripts/create_deployment_tx.ts --network mainnet

# 5. Sign with required signers
# Use Gnosis Safe UI: https://app.safe.global/

# 6. Execute deployment
# Wait for multi-sig approval and execution

# 7. Verify contracts on Etherscan
npx hardhat verify --network mainnet $CONTRACT_ADDRESS "constructor" "args"

# 8. Initialize contracts
npx hardhat run scripts/initialize.ts --network mainnet

# 9. Transfer ownership to multi-sig
npx hardhat run scripts/transfer_ownership.ts --network mainnet

# 10. Monitor deployment
npx hardhat run scripts/monitor_deployment.js --network mainnet --duration 3600
```

#### Upgrade Contracts (Proxy Pattern)
```bash
# For upgradeable contracts using OpenZeppelin

# 1. Prepare new implementation
npx hardhat compile

# 2. Test upgrade locally
npx hardhat run scripts/test_upgrade.ts --network localhost

# 3. Deploy new implementation
npx hardhat run scripts/deploy_implementation.ts --network mainnet

# Output: New implementation at 0xnew...

# 4. Create upgrade proposal (via governance)
npx hardhat run scripts/create_upgrade_proposal.ts --network mainnet \
  --proxy 0xproxy... \
  --implementation 0xnew...

# 5. Vote on proposal (multi-sig)
# Voting period: 3 days

# 6. Execute upgrade (after timelock)
npx hardhat run scripts/execute_upgrade.ts --network mainnet \
  --proposal-id 42

# 7. Verify upgrade
npx hardhat run scripts/verify_upgrade.ts --network mainnet
```

### Contract Interaction Operations

#### Call Contract Functions
```bash
# Read functions (no gas)
cast call $CONTRACT_ADDRESS "balanceOf(address)" $USER_ADDRESS --rpc-url $RPC_URL

# Write functions (requires gas)
cast send $CONTRACT_ADDRESS "stake(uint256)" 1000000000000000000 \
  --private-key $PRIVATE_KEY \
  --rpc-url $RPC_URL

# Via Hardhat
npx hardhat run scripts/interact.ts --network mainnet
```

#### Monitor Events
```bash
# Listen for events
npx hardhat run scripts/listen_events.js --network mainnet

# Example event listener script:
cat > scripts/listen_events.js << 'EOF'
const { ethers } = require("hardhat");

async function main() {
  const contract = await ethers.getContractAt("StakingContract", "0x123...");

  contract.on("Staked", (user, amount, event) => {
    console.log(`Staked: ${user} staked ${ethers.utils.formatEther(amount)} ETH`);
  });

  contract.on("Unstaked", (user, amount, event) => {
    console.log(`Unstaked: ${user} unstaked ${ethers.utils.formatEther(amount)} ETH`);
  });

  console.log("Listening for events...");
}

main();
EOF

# Query past events
cast logs --from-block 12345678 --to-block latest \
  --address $CONTRACT_ADDRESS \
  "Staked(address indexed,uint256)" \
  --rpc-url $RPC_URL
```

### Multi-sig Operations

#### Create Transaction Proposal
```bash
# Using Gnosis Safe CLI
safe-cli --safe-address 0x789... \
  propose-tx \
  --to $CONTRACT_ADDRESS \
  --value 0 \
  --data $(cast calldata "withdraw(uint256)" 1000000000000000000) \
  --description "Withdraw 1 ETH from treasury"

# Or via web UI: https://app.safe.global/
```

#### Approve and Execute
```bash
# Signer 1 approves
safe-cli --safe-address 0x789... approve-tx --tx-nonce 42

# Signer 2 approves
safe-cli --safe-address 0x789... approve-tx --tx-nonce 42

# Execute (once threshold reached)
safe-cli --safe-address 0x789... execute-tx --tx-nonce 42

# Verify execution
cast tx $TX_HASH --rpc-url $RPC_URL
```

### Oracle Management

#### Check Chainlink Price Feed
```bash
# Get latest price
PRICE=$(cast call $CHAINLINK_FEED "latestAnswer()" --rpc-url $RPC_URL)
echo "Latest price: $PRICE"

# Check update timestamp
TIMESTAMP=$(cast call $CHAINLINK_FEED "latestTimestamp()" --rpc-url $RPC_URL)
echo "Last updated: $(date -d @$TIMESTAMP)"

# Get round data
cast call $CHAINLINK_FEED "latestRoundData()" --rpc-url $RPC_URL
```

#### Switch to Backup Oracle
```bash
# Emergency: Switch to backup feed
npx hardhat run scripts/switch_oracle.ts --network mainnet \
  --new-feed $BACKUP_CHAINLINK_FEED

# Verify switch
npx hardhat run scripts/verify_oracle.ts --network mainnet
```

---

## Incident Response

### Detection

**Automated Detection:**
- Contract monitoring service alerts
- Treasury balance alerts
- Transaction failure rate monitoring
- Gas price alerts
- Oracle data freshness checks

**Manual Detection:**
```bash
# Check contract status
npx hardhat run scripts/health_check.js --network mainnet

# Check recent transactions
curl "https://api.etherscan.io/api?module=account&action=txlist&address=$CONTRACT&apikey=$ETHERSCAN_API_KEY" | jq '.result[-10:]'

# Check for exploit patterns
npx hardhat run scripts/security_scan.js --network mainnet
```

### Triage

#### Severity Classification

### P0: Critical Security Incident
- Contract exploit detected
- Treasury drained
- Unauthorized access to admin functions
- Contract permanently locked

### P1: Major Issue
- High transaction failure rate (> 20%)
- Oracle data stale > 1 hour
- Suspicious activity detected
- Contract paused unexpectedly

### P2: Degraded Service
- High gas prices preventing transactions
- Non-critical function failures
- Event emission issues
- UI/frontend issues

### P3: Minor Issue
- Cosmetic issues
- Documentation discrepancies
- Minor optimization opportunities

### Incident Response Procedures

#### P0: Contract Exploit Detected

**Immediate Actions (0-5 minutes):**
```bash
# 1. PAUSE CONTRACT (if pause mechanism exists)
npx hardhat run scripts/emergency_pause.ts --network mainnet

# Or via multi-sig
safe-cli --safe-address $MULTISIG \
  propose-tx \
  --to $CONTRACT \
  --data $(cast calldata "pause()") \
  --description "EMERGENCY PAUSE - EXPLOIT DETECTED"

# 2. Notify team immediately
./scripts/send_emergency_alert.sh "CONTRACT EXPLOIT DETECTED"

# 3. Document evidence
npx hardhat run scripts/collect_evidence.js --network mainnet > evidence.json

# 4. Check treasury and user balances
npx hardhat run scripts/check_balances.js --network mainnet

# 5. Identify exploit transaction
curl "https://api.etherscan.io/api?module=account&action=txlist&address=$CONTRACT&apikey=$ETHERSCAN_API_KEY" | \
  jq '.result[-50:]' > recent_txs.json
```

**Investigation (5-30 minutes):**
```bash
# 1. Analyze exploit transaction
EXPLOIT_TX="0xabc..."
cast tx $EXPLOIT_TX --rpc-url $RPC_URL
cast run $EXPLOIT_TX --rpc-url $RPC_URL --trace

# 2. Identify vulnerability
slither contracts/ --detect all

# 3. Estimate damages
npx hardhat run scripts/assess_damage.js --network mainnet

# 4. Check if other contracts affected
npx hardhat run scripts/check_all_contracts.js --network mainnet

# 5. Prepare mitigation plan
cat > mitigation_plan.md << 'EOF'
# Exploit Mitigation Plan

## Vulnerability
[Description of the vulnerability]

## Immediate Actions
- [x] Contract paused
- [ ] Deploy patched contract
- [ ] Migration plan for user funds
- [ ] Communication to users

## Timeline
- T+0: Exploit detected, contract paused
- T+1h: Patch developed and tested
- T+3h: Deploy fix, begin migration
- T+24h: Complete user fund recovery

EOF
```

**Mitigation:**
```bash
# 1. Develop and test fix
# Fix vulnerability in code
vim contracts/StakingContract.sol

# Test thoroughly
npx hardhat test
slither contracts/

# 2. Deploy fixed contract
npx hardhat run scripts/deploy_fixed.ts --network mainnet

# 3. Migrate user funds (if necessary)
npx hardhat run scripts/migrate_funds.ts --network mainnet

# 4. Verify fix
npx hardhat run scripts/verify_fix.ts --network mainnet

# 5. Resume operations
npx hardhat run scripts/unpause.ts --network mainnet

# 6. Monitor closely
npx hardhat run scripts/monitor_post_incident.js --network mainnet --duration 86400
```

**Post-Incident:**
```bash
# 1. Conduct post-mortem
cat > post_mortem.md << 'EOF'
# Security Incident Post-Mortem

**Date:** $(date)
**Severity:** P0
**Duration:** 4 hours

## Timeline
- 10:00: Exploit detected
- 10:02: Contract paused
- 10:30: Vulnerability identified
- 12:00: Fix deployed
- 14:00: User funds migrated, service restored

## Root Cause
Reentrancy vulnerability in withdraw function

## Impact
- $50,000 stolen
- 4 hours downtime
- 100 users affected

## Action Items
- [ ] Reimburse affected users
- [ ] External audit of all contracts
- [ ] Implement additional security checks
- [ ] Update monitoring and alerts
- [ ] Improve incident response procedures

EOF

# 2. Notify users and stakeholders
./scripts/send_incident_report.sh

# 3. File insurance claim (if applicable)
./scripts/file_insurance_claim.sh

# 4. Schedule external audit
# Contact audit firms
```

#### P1: High Transaction Failure Rate

**Investigation:**
```bash
# Check recent failures
curl "https://api.etherscan.io/api?module=account&action=txlist&address=$CONTRACT&apikey=$ETHERSCAN_API_KEY" | \
  jq '.result[-100:] | map(select(.isError=="1"))'

# Check gas prices
curl "https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=$ETHERSCAN_API_KEY"

# Test contract locally
npx hardhat test

# Check for contract state issues
npx hardhat run scripts/check_state.js --network mainnet
```

**Mitigation:**
```bash
# If gas price issue
# Notify users to wait for lower gas
./scripts/notify_users.sh "High gas prices, please wait"

# If contract issue
# Investigate and fix
npx hardhat run scripts/diagnose.js --network mainnet

# If necessary, pause and fix
npx hardhat run scripts/emergency_pause.ts --network mainnet
```

#### P1: Oracle Data Stale

**Investigation:**
```bash
# Check oracle timestamp
TIMESTAMP=$(cast call $CHAINLINK_FEED "latestTimestamp()" --rpc-url $RPC_URL)
CURRENT=$(date +%s)
AGE=$((CURRENT - TIMESTAMP))
echo "Oracle data age: ${AGE}s"

# Check Chainlink network status
curl https://status.chain.link/

# Verify oracle contract
cast code $CHAINLINK_FEED --rpc-url $RPC_URL
```

**Mitigation:**
```bash
# Switch to backup oracle
npx hardhat run scripts/switch_oracle.ts --network mainnet \
  --new-feed $BACKUP_FEED

# Or pause operations until oracle recovers
npx hardhat run scripts/emergency_pause.ts --network mainnet

# Monitor oracle recovery
while true; do
  TIMESTAMP=$(cast call $CHAINLINK_FEED "latestTimestamp()" --rpc-url $RPC_URL)
  CURRENT=$(date +%s)
  AGE=$((CURRENT - TIMESTAMP))
  echo "Oracle age: ${AGE}s"
  if [ $AGE -lt 300 ]; then
    echo "Oracle recovered"
    break
  fi
  sleep 60
done
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: "Out of Gas" Errors

**Symptoms:**
```
Error: Transaction ran out of gas
```

**Diagnosis:**
```bash
# Estimate gas for transaction
cast estimate $CONTRACT "functionName(args...)" --rpc-url $RPC_URL

# Check gas limit in code
grep "gas:" scripts/deploy.ts
```

**Solution:**
```bash
# Increase gas limit in transaction
cast send $CONTRACT "functionName()" --gas-limit 500000 --rpc-url $RPC_URL

# Or optimize contract code to reduce gas
# Use gas-efficient patterns
# Avoid loops, minimize storage writes
```

---

#### Issue: Contract Verification Failed

**Symptoms:**
```
Error: Contract verification failed on Etherscan
```

**Diagnosis:**
```bash
# Check compiler settings
cat hardhat.config.ts

# Check constructor arguments
npx hardhat run scripts/get_constructor_args.js
```

**Solution:**
```bash
# Retry verification with correct parameters
npx hardhat verify --network mainnet $CONTRACT_ADDRESS \
  --constructor-args scripts/constructor-args.js

# Or verify via API
curl -X POST "https://api.etherscan.io/api" \
  -d "module=contract" \
  -d "action=verifysourcecode" \
  -d "contractaddress=$CONTRACT_ADDRESS" \
  -d "sourceCode=$(cat contracts/flattened.sol)" \
  -d "contractname=StakingContract" \
  -d "compilerversion=v0.8.20+commit.a1b79de6" \
  -d "apikey=$ETHERSCAN_API_KEY"
```

---

## Maintenance Procedures

### Daily Tasks

```bash
# Morning health check
npx hardhat run scripts/health_check.js --network mainnet

# Check transaction activity
curl "https://api.etherscan.io/api?module=account&action=txlist&address=$CONTRACT&apikey=$ETHERSCAN_API_KEY" | \
  jq '.result[-20:]'

# Monitor gas prices
cast gas-price --rpc-url $RPC_URL

# Check treasury balance
cast balance $TREASURY --rpc-url $RPC_URL

# Review events
npx hardhat run scripts/get_daily_events.js --network mainnet
```

### Weekly Tasks

```bash
# Review contract analytics
npx hardhat run scripts/weekly_report.js --network mainnet

# Check for security updates
npm audit
npm outdated

# Review pending proposals
npx hardhat run scripts/list_proposals.js --network mainnet

# Backup contract state
npx hardhat run scripts/export_state.js --network mainnet > backups/state-$(date +%Y%m%d).json
```

### Monthly Tasks

```bash
# Comprehensive security audit
slither contracts/ --exclude-dependencies
npm audit

# Review gas optimization opportunities
npx hardhat run scripts/analyze_gas.js --network mainnet

# Update dependencies (carefully)
npm update

# Re-run full test suite
npx hardhat test
npx hardhat coverage

# Review and update documentation
vim docs/operations.md
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO**: 0 (blockchain is immutable and replicated)
- **RTO**:
  - Emergency pause: < 5 minutes
  - Deploy fix: < 2 hours
  - Complete recovery: < 24 hours

### Backup Strategy

```bash
# Contract code is backed up in Git
git push origin main

# Contract state can be reconstructed from blockchain
# Export important state periodically
npx hardhat run scripts/export_state.js --network mainnet > backups/state-$(date +%Y%m%d).json

# Multi-sig wallet is non-custodial (keys held by multiple parties)
# Document multi-sig signers and recovery procedures
```

### Emergency Procedures

**Contract Pausable:**
```bash
# Pause all operations
npx hardhat run scripts/emergency_pause.ts --network mainnet
```

**Fund Recovery:**
```bash
# If contract has recovery mechanism
npx hardhat run scripts/recover_funds.ts --network mainnet --destination $SAFE_ADDRESS
```

---

## Quick Reference Card

### Most Common Operations

```bash
# Compile contracts
npx hardhat compile

# Run tests
npx hardhat test

# Deploy to testnet
npx hardhat run scripts/deploy.ts --network goerli

# Verify contract
npx hardhat verify --network mainnet $ADDRESS "args"

# Check contract status
npx hardhat run scripts/health_check.js --network mainnet

# Pause contract
npx hardhat run scripts/emergency_pause.ts --network mainnet

# Monitor events
npx hardhat run scripts/listen_events.js --network mainnet
```

### Emergency Response

```bash
# P0: Exploit detected
npx hardhat run scripts/emergency_pause.ts --network mainnet

# P0: Treasury at risk
safe-cli --safe-address $MULTISIG propose-tx --to $TREASURY --data $(cast calldata "pause()")

# P1: Oracle stale
npx hardhat run scripts/switch_oracle.ts --network mainnet --new-feed $BACKUP

# P1: High tx failures
npx hardhat run scripts/diagnose.js --network mainnet
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Blockchain Engineering Team
- **Review Schedule:** Monthly or after security incidents
- **Feedback:** Create issue or submit PR with updates
- **Security Contact:** security@example.com
