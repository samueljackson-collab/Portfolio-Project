# Portfolio Projects - Technology & Dependencies Matrix

## Quick Reference Guide

### Project Quick Lookup Table

| # | Project Name | Primary Tech | Secondary Tech | Status | Files | AWS | K8s | Cloud |
|---|---|---|---|---|---|---|---|---|
| 1 | AWS Infrastructure | Terraform | AWS CDK, Pulumi | 75% | 17 | Yes | Yes | AWS |
| 2 | Database Migration | Python | Debezium, Postgres | 40% | 3 | No | No | On-prem |
| 3 | K8s CI/CD | GitHub Actions | ArgoCD | 35% | 2 | No | Yes | Any |
| 4 | DevSecOps | GitHub Actions | SBOM, Scanning | 25% | 2 | No | Yes | Any |
| 5 | Data Streaming | Python | Kafka, Flink | 40% | 3 | No | No | On-prem |
| 6 | MLOps Platform | Python | MLflow, Optuna | 60% | 6 | Yes | Yes | Multi |
| 7 | Serverless Data | Python | AWS SAM | 50% | 6 | Yes | No | AWS/Azure |
| 8 | AI Chatbot | Python | FastAPI, LLM | 55% | 5 | Yes | No | AWS/Azure |
| 9 | Disaster Recovery | Terraform | AWS | 60% | 6 | Yes | Yes | AWS |
| 10 | Blockchain Smart | Solidity | Hardhat | 70% | 8 | No | No | Blockchain |
| 11 | IoT Analytics | Python | MQTT, AWS IoT | 45% | 4 | Yes | No | AWS |
| 12 | Quantum Computing | Python | Qiskit | 50% | 4 | Yes | No | AWS |
| 13 | Cybersecurity SOAR | Python | Threat Intel APIs | 45% | 4 | No | No | On-prem |
| 14 | Edge AI | Python | ONNX Runtime | 50% | 4 | No | No | Azure/Edge |
| 15 | Collaboration | Python | WebSocket, CRDT | 50% | 4 | No | No | On-prem |
| 16 | Data Lake | Python | Databricks, Delta | 55% | 5 | No | No | Databricks |
| 17 | Service Mesh | YAML | Istio, Consul | 40% | 3 | Yes | Yes | Multi-Cloud |
| 18 | GPU Computing | Python | CUDA, Dask | 45% | 4 | Yes | No | GPU Cloud |
| 19 | K8s Operators | Python | Kopf | 50% | 4 | No | Yes | K8s |
| 20 | Oracle Service | Solidity | Chainlink, Node.js | 50% | 4 | No | No | Blockchain |
| 21 | Quantum Crypto | Python | Kyber, ECDH | 50% | 4 | No | No | On-prem |
| 22 | Autonomous DevOps | Python | Event-driven | 40% | 3 | Yes | Yes | Multi |
| 23 | Monitoring | YAML | Prometheus, Grafana | 55% | 3 | No | Yes | K8s |
| 24 | Report Generator | Python | Jinja2, WeasyPrint | 60% | 5 | No | No | On-prem |
| 25 | Portfolio Website | Node.js | VitePress | 50% | 4 | No | No | Static |

---

## Technology Dependencies by Project

### Projects Using AWS
**Projects**: 1, 6, 7, 8, 9, 11, 12, 18, 22
**Key Services**:
- EC2, ECS, Fargate
- Lambda, API Gateway
- RDS, DynamoDB
- S3, CloudWatch
- IAM, Secrets Manager
- SageMaker, Batch
- IoT Core, Kinesis Firehose

**Setup Requirements**:
```bash
# AWS CLI configuration
aws configure
# or
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
export AWS_DEFAULT_REGION=us-east-1
```

---

### Projects Using Kubernetes
**Projects**: 1, 3, 6, 9, 17, 19, 23
**Key Tools**:
- kubectl
- Helm
- Kustomize
- ArgoCD
- Istio
- Prometheus/Grafana

**Setup Requirements**:
```bash
# Kubernetes cluster (EKS, GKE, or local)
kubectl config use-context <cluster>
kubectl get nodes

# Additional tools
helm repo add <repo>
kubectl apply -k overlays/production
```

---

### Python Projects with ML/Data
**Projects**: 5, 6, 8, 12, 13, 14, 15, 16, 18, 19, 21, 22
**Common Libraries**:
- numpy, pandas, scikit-learn
- TensorFlow, PyTorch
- Flask, FastAPI
- SQLAlchemy, psycopg2
- Kafka-python, pyspark
- boto3 (AWS SDK)

**Setup Template**:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### Blockchain Projects
**Projects**: 10, 20
**Key Technologies**:
- Solidity (smart contracts)
- Hardhat (development framework)
- Ethers.js / Web3.js
- Chainlink (oracle network)
- OpenZeppelin (security libraries)
- Ethereum network (testnet/mainnet)

**Setup Requirements**:
```bash
npm install
# Create .env with private keys
npx hardhat compile
npx hardhat test
```

---

### Infrastructure/IaC Projects
**Projects (3 total)**: 1, 9, 17
**Key Technologies**:
- Terraform/HCL
- AWS CDK (Python)
- Pulumi (Python/Go)
- Helm charts
- CloudFormation

**Setup Requirements**:
```bash
# Terraform
terraform init
terraform plan -var-file=prod.tfvars
terraform apply

# AWS CDK
cdk bootstrap
cdk deploy

# Pulumi
pulumi stack init prod
pulumi up
```

---

### Database Technologies
**Projects Using Databases**:
- PostgreSQL: 1, 2, 9, 11
- DynamoDB: 7, 8
- TimescaleDB: 11
- Databricks/Delta Lake: 16

**Setup Examples**:
```bash
# PostgreSQL
docker run -e POSTGRES_PASSWORD=password postgres:14
psql -U postgres -d portfolio

# TimescaleDB
docker run -e POSTGRES_PASSWORD=password timescale/timescaledb:latest-pg14

# DynamoDB Local
docker run -p 8000:8000 amazon/dynamodb-local
```

---

## Missing Dependencies Checklist

### For Each Project, Verify:

#### Infrastructure/Config
- [ ] README.md present and accurate
- [ ] .env.example or secrets template
- [ ] Configuration files (tfvars, yaml, json)
- [ ] Docker/Container setup (if applicable)
- [ ] Cloud provider credentials setup

#### Code & Testing
- [ ] Source code in src/ directory
- [ ] Unit tests present
- [ ] Integration tests present
- [ ] Test data/fixtures
- [ ] Mock/stub implementations

#### Documentation
- [ ] API documentation
- [ ] Architecture diagrams
- [ ] Deployment guide
- [ ] Troubleshooting guide
- [ ] Example configurations

#### Deployment
- [ ] Dockerfile (if containerized)
- [ ] docker-compose.yml (if local dev)
- [ ] Kubernetes manifests (if K8s)
- [ ] Terraform/CDK code (if IaC)
- [ ] Deployment scripts

---

## Technology Installation Guide

### Required Base Tools
All projects require:
- Git
- Python 3.8+ (19 projects)
- Node.js 16+ (3 projects)
- Docker & Docker Compose (recommended for all)

### Project-Specific Tools

**For AWS Projects** (1,6,7,8,9,11,12,18,22):
```bash
pip install boto3 awscli
aws configure
```

**For Terraform Projects** (1,9,17):
```bash
# Download from terraform.io
terraform version
# Should be 1.0+
```

**For Kubernetes Projects** (1,3,6,9,17,19,23):
```bash
# Install kubectl
kubectl version --client
# Install helm
helm version
# Install kind or minikube for local testing
kind create cluster
```

**For Blockchain Projects** (10,20):
```bash
npm install -g hardhat
npm install ethers @nomiclabs/hardhat-ethers
```

**For Python ML Projects** (6,12,18):
```bash
pip install mlflow optuna torch scikit-learn
```

**For Data Projects** (5,11,16):
```bash
pip install kafka-python pyspark pandas
```

---

## Environment Variables Template

### For AWS Projects
```bash
# .env.example
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1
AWS_PROFILE=default
```

### For Blockchain Projects
```bash
# .env.example
PRIVATE_KEY=your_private_key_hex
NETWORK_RPC_URL=https://eth-goerli.alchemyapi.io/v2/YOUR_API_KEY
ETHERSCAN_API_KEY=your_key
```

### For Azure Projects
```bash
# .env.example
AZURE_SUBSCRIPTION_ID=xxx
AZURE_TENANT_ID=xxx
AZURE_CLIENT_ID=xxx
AZURE_CLIENT_SECRET=xxx
```

### For LLM Projects (8, 24, 25)
```bash
# .env.example
OPENAI_API_KEY=sk-xxx
PINECONE_API_KEY=xxx
PINECONE_ENVIRONMENT=xxx
```

---

## Quick Start Commands by Project

### Project 1: AWS Infrastructure
```bash
cd projects/1-aws-infrastructure-automation
terraform init -backend-config=terraform/backend.hcl
terraform plan -var-file=terraform/dev.tfvars
# Review and apply
```

### Project 2: Database Migration
```bash
cd projects/2-database-migration
pip install -r requirements.txt
# Setup PostgreSQL instances
python src/migration_orchestrator.py
```

### Project 5: Data Streaming
```bash
cd projects/5-real-time-data-streaming
docker-compose up  # Kafka + Zookeeper
pip install -r requirements.txt
python src/process_events.py
```

### Project 6: MLOps
```bash
cd projects/6-mlops-platform
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mlflow server --backend-store-uri sqlite:///mlruns.db
./scripts/run_training.sh configs/churn-experiment.yaml
```

### Project 8: AI Chatbot
```bash
cd projects/8-advanced-ai-chatbot
pip install -r requirements.txt
# Setup Pinecone API key in .env
python -m uvicorn src.chatbot_service:app --reload
```

### Project 10: Blockchain Smart Contracts
```bash
cd projects/10-blockchain-smart-contract-platform
npm install
npx hardhat compile
npx hardhat test
npx hardhat run scripts/deploy.ts --network goerli
```

### Project 23: Monitoring
```bash
cd projects/23-advanced-monitoring
# Deploy to Kubernetes
kubectl apply -k manifests/base
kubectl apply -k manifests/overlays/production
# Access Grafana at localhost:3000
```

### Project 25: Portfolio Website
```bash
cd projects/25-portfolio-website
npm install
npm run docs:dev
# Opens at http://localhost:5173
```

---

## Estimated Time to Full Completion (by project)

| Project | Current | To 90% | To 100% | 
|---------|---------|---------|---------|
| 1 | 75% | 2 days | 3 days |
| 2 | 40% | 4 days | 5 days |
| 3 | 35% | 5 days | 6 days |
| 4 | 25% | 6 days | 8 days |
| 5 | 40% | 4 days | 5 days |
| 6 | 60% | 3 days | 4 days |
| 7 | 50% | 3 days | 5 days |
| 8 | 55% | 3 days | 4 days |
| 9 | 60% | 2 days | 4 days |
| 10 | 70% | 2 days | 3 days |
| 11 | 45% | 4 days | 5 days |
| 12 | 50% | 3 days | 5 days |
| 13 | 45% | 4 days | 5 days |
| 14 | 50% | 3 days | 4 days |
| 15 | 50% | 3 days | 5 days |
| 16 | 55% | 3 days | 4 days |
| 17 | 40% | 4 days | 6 days |
| 18 | 45% | 4 days | 5 days |
| 19 | 50% | 3 days | 4 days |
| 20 | 50% | 3 days | 4 days |
| 21 | 50% | 3 days | 4 days |
| 22 | 40% | 4 days | 6 days |
| 23 | 55% | 3 days | 4 days |
| 24 | 60% | 2 days | 3 days |
| 25 | 50% | 3 days | 4 days |

**Total Estimated Effort**: ~90 days for all projects to 100%
