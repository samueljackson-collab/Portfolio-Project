# Runbook — Project 8 (Advanced AI Chatbot)

## Overview

Production operations runbook for the Advanced AI Chatbot with Retrieval-Augmented Generation (RAG). This runbook covers FastAPI service operations, vector store management, LLM integration, tool orchestration, and troubleshooting for the chatbot service.

**System Components:**
- FastAPI Gateway (REST API + WebSocket streaming)
- Vector Store (OpenSearch/Pinecone for semantic search)
- Large Language Model (OpenAI/Azure OpenAI/local inference)
- Tool Orchestrator (knowledge graph, deployment automation, analytics)
- Memory Manager (conversation history + knowledge base)
- Guardrail Middleware (content filtering, rate limiting)
- ECS/Fargate (containerized deployment)
- CloudWatch (monitoring and logging)

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **API availability** | 99.9% | Uptime of FastAPI service |
| **Response latency (p95)** | < 3 seconds | Time from question → first token |
| **Streaming latency (TTFT)** | < 500ms | Time to first token in streaming response |
| **Vector search latency** | < 100ms | Semantic search query time |
| **LLM success rate** | 99% | Successful completions without errors |
| **Tool execution success rate** | 95% | Tool calls completed successfully |
| **Context relevance score** | > 0.7 | Relevance of retrieved context to query |

---

## Dashboards & Alerts

### Dashboards

#### FastAPI Service Dashboard
```bash
# Check service health
curl -f http://localhost:8000/health || echo "Service down"

# Check metrics endpoint
curl http://localhost:8000/metrics

# View service status
docker ps | grep chatbot-service
# or for ECS:
aws ecs describe-services \
  --cluster chatbot-cluster \
  --services chatbot-service
```

#### Vector Store Dashboard
```bash
# Check OpenSearch cluster health
curl -XGET "https://search-domain.us-east-1.es.amazonaws.com/_cluster/health?pretty"

# Check index statistics
curl -XGET "https://search-domain.us-east-1.es.amazonaws.com/knowledge-base/_stats?pretty"

# For Pinecone:
curl -X GET "https://api.pinecone.io/indexes/knowledge-base/describe" \
  -H "Api-Key: $PINECONE_API_KEY"
```

#### LLM Usage Dashboard
```bash
# Check OpenAI API usage
curl https://api.openai.com/v1/dashboard/billing/usage \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# View token usage logs
python scripts/analyze_token_usage.py --days 7

# Check rate limits
python scripts/check_rate_limits.py
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | FastAPI service down | Immediate | Restart service, check logs |
| **P0** | Vector store unreachable | Immediate | Check connectivity, failover if available |
| **P1** | LLM API errors > 5% | 15 minutes | Check API status, switch providers if needed |
| **P1** | Response latency > 10s (p95) | 15 minutes | Scale service, optimize queries |
| **P2** | Tool execution failures > 10% | 30 minutes | Investigate tool integrations |
| **P2** | Memory usage > 80% | 30 minutes | Scale service, clear cache |
| **P3** | Context relevance < 0.5 | 1 hour | Review embeddings, retune search |

#### Alert Queries

```bash
# Check service health
if ! curl -sf http://localhost:8000/health; then
  echo "ALERT: FastAPI service unreachable"
fi

# Check error rate
ERROR_COUNT=$(grep -c "ERROR" logs/chatbot.log)
if [ $ERROR_COUNT -gt 10 ]; then
  echo "ALERT: High error rate detected: $ERROR_COUNT errors"
fi

# Check response times
python scripts/check_latency.py --threshold 3000  # 3 seconds
```

---

## Standard Operations

### FastAPI Service Management

#### Start Service Locally
```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Set environment variables
export OPENAI_API_KEY="sk-..."
export VECTOR_STORE_URL="https://search-domain.us-east-1.es.amazonaws.com"
export VECTOR_STORE_INDEX="knowledge-base"

# 3. Start service
uvicorn src.chatbot_service:app --host 0.0.0.0 --port 8000 --reload

# 4. Verify startup
curl http://localhost:8000/health
```

#### Deploy to ECS
```bash
# 1. Build Docker image
docker build -t chatbot-service:v1.0 -f Dockerfile .

# 2. Tag and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker tag chatbot-service:v1.0 123456789.dkr.ecr.us-east-1.amazonaws.com/chatbot-service:v1.0
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/chatbot-service:v1.0

# 3. Update task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# 4. Update service
aws ecs update-service \
  --cluster chatbot-cluster \
  --service chatbot-service \
  --task-definition chatbot-service:2 \
  --force-new-deployment

# 5. Monitor deployment
aws ecs wait services-stable \
  --cluster chatbot-cluster \
  --services chatbot-service

# 6. Verify deployment
TASK_ARN=$(aws ecs list-tasks --cluster chatbot-cluster --service chatbot-service --query 'taskArns[0]' --output text)
aws ecs describe-tasks --cluster chatbot-cluster --tasks $TASK_ARN
```

#### Scale Service
```bash
# Scale ECS service
aws ecs update-service \
  --cluster chatbot-cluster \
  --service chatbot-service \
  --desired-count 5

# Enable auto-scaling
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/chatbot-cluster/chatbot-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/chatbot-cluster/chatbot-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration \
    'PredefinedMetricSpecification={PredefinedMetricType=ECSServiceAverageCPUUtilization},TargetValue=70.0'
```

### Vector Store Operations

#### Index Documents
```bash
# 1. Prepare documents
python scripts/prepare_documents.py \
  --source data/knowledge_base/ \
  --output data/processed/

# 2. Generate embeddings
python scripts/generate_embeddings.py \
  --input data/processed/ \
  --model text-embedding-ada-002 \
  --batch-size 100

# 3. Index to vector store
python scripts/index_documents.py \
  --embeddings data/embeddings/ \
  --vector-store opensearch \
  --index knowledge-base

# 4. Verify indexing
python scripts/verify_index.py --index knowledge-base
```

#### Update Index
```bash
# Add new documents
python scripts/add_documents.py \
  --documents data/new_docs/ \
  --index knowledge-base

# Delete documents
python scripts/delete_documents.py \
  --doc-ids "doc1,doc2,doc3" \
  --index knowledge-base

# Rebuild index (if schema changes)
python scripts/rebuild_index.py \
  --old-index knowledge-base \
  --new-index knowledge-base-v2 \
  --reindex

# Alias swap for zero-downtime update
curl -XPOST "https://search-domain/_aliases" -H 'Content-Type: application/json' -d '{
  "actions": [
    {"remove": {"index": "knowledge-base-v1", "alias": "knowledge-base"}},
    {"add": {"index": "knowledge-base-v2", "alias": "knowledge-base"}}
  ]
}'
```

#### Query Vector Store
```bash
# Test semantic search
python scripts/test_search.py \
  --query "How do I deploy a model?" \
  --top-k 5

# Example output:
# Top 5 results:
# 1. (score: 0.89) MLOps deployment guide...
# 2. (score: 0.85) Kubernetes deployment...
# 3. (score: 0.82) SageMaker deployment...
# 4. (score: 0.78) Lambda deployment...
# 5. (score: 0.75) Docker deployment...

# Benchmark search performance
python scripts/benchmark_search.py \
  --queries test/queries.txt \
  --iterations 100
```

### LLM Integration Management

#### Test LLM Connection
```bash
# Test OpenAI API
python scripts/test_llm.py \
  --provider openai \
  --model gpt-4 \
  --prompt "Hello, how are you?"

# Test Azure OpenAI
python scripts/test_llm.py \
  --provider azure \
  --model gpt-4 \
  --endpoint https://your-resource.openai.azure.com/ \
  --prompt "Hello, how are you?"

# Test local model (GPT4All/Llama.cpp)
python scripts/test_llm.py \
  --provider local \
  --model llama-2-7b \
  --prompt "Hello, how are you?"
```

#### Switch LLM Provider
```bash
# Update environment variables
export LLM_PROVIDER="azure"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_DEPLOYMENT="gpt-4"

# Restart service
kubectl rollout restart deployment/chatbot-service -n chatbot

# Or for ECS:
aws ecs update-service \
  --cluster chatbot-cluster \
  --service chatbot-service \
  --force-new-deployment

# Verify switch
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What provider are you using?", "conversation_id": "test"}'
```

#### Monitor LLM Usage
```bash
# Check token usage
python scripts/get_token_usage.py --date $(date +%Y-%m-%d)

# Expected output:
# Date: 2025-11-10
# Total tokens: 1,234,567
# Prompt tokens: 823,456
# Completion tokens: 411,111
# Estimated cost: $12.34

# Check rate limit status
python scripts/check_rate_limits.py

# Set usage alerts
python scripts/set_usage_alert.py --threshold 1000000 --email ops@example.com
```

### Tool Orchestration

#### Register New Tool
```bash
# Create tool definition
cat > tools/deploy_tool.py << 'EOF'
from typing import Dict, Any

def deploy_model(model_name: str, environment: str) -> Dict[str, Any]:
    """Deploy a model to specified environment"""
    # Implementation
    return {"status": "success", "endpoint": "https://..."}

TOOL_SPEC = {
    "name": "deploy_model",
    "description": "Deploy a trained model to production environment",
    "parameters": {
        "model_name": {"type": "string", "required": True},
        "environment": {"type": "string", "enum": ["staging", "production"]}
    }
}
EOF

# Register tool
python scripts/register_tool.py --tool tools/deploy_tool.py

# Test tool
python scripts/test_tool.py \
  --tool-name deploy_model \
  --params '{"model_name": "churn-classifier", "environment": "staging"}'

# Restart service to load new tool
kubectl rollout restart deployment/chatbot-service -n chatbot
```

#### Monitor Tool Execution
```bash
# View tool execution logs
python scripts/view_tool_logs.py --last 100

# Check tool success rates
python scripts/tool_metrics.py --days 7

# Example output:
# Tool: deploy_model
#   Success: 95.2%
#   Failures: 4.8%
#   Avg duration: 2.3s
# Tool: query_analytics
#   Success: 98.5%
#   Failures: 1.5%
#   Avg duration: 0.8s
```

### Memory and Conversation Management

#### View Conversation History
```bash
# Get conversation
python scripts/get_conversation.py --conversation-id "abc123"

# Export conversation
python scripts/export_conversation.py \
  --conversation-id "abc123" \
  --format json \
  > conversation.json

# List active conversations
python scripts/list_conversations.py --status active --limit 20
```

#### Clear Old Conversations
```bash
# Archive conversations older than 30 days
python scripts/archive_conversations.py --older-than 30

# Delete archived conversations
python scripts/delete_conversations.py --status archived --older-than 90

# Verify cleanup
python scripts/conversation_stats.py
```

---

## Incident Response

### Detection

**Automated Detection:**
- Health check failures
- High error rates in logs
- Elevated response latency
- LLM API failures
- Vector store connectivity issues

**Manual Detection:**
```bash
# Check service health
curl http://localhost:8000/health

# Check recent errors
tail -100 logs/chatbot.log | grep ERROR

# Check container status
docker ps | grep chatbot
# or
aws ecs describe-services --cluster chatbot-cluster --services chatbot-service

# Test chat functionality
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "conversation_id": "test"}'
```

### Triage

#### Severity Classification

**P0: Complete Outage**
- FastAPI service completely down
- Vector store unreachable
- All LLM requests failing
- Database connection failure

**P1: Degraded Service**
- High error rate (> 10%)
- Response latency > 10 seconds
- LLM API partially failing
- Tool execution failures > 20%

**P2: Warning State**
- Elevated latency (> 5 seconds)
- Some tool failures
- Memory usage high
- Occasional LLM timeouts

**P3: Informational**
- Single conversation failure
- Minor latency increase
- Low context relevance score

### Incident Response Procedures

#### P0: FastAPI Service Down

**Immediate Actions (0-2 minutes):**
```bash
# 1. Check if process is running
ps aux | grep uvicorn
docker ps | grep chatbot-service

# 2. Check logs for crash reason
tail -100 logs/chatbot.log
docker logs chatbot-service --tail 100

# 3. Restart service
# Local:
pkill uvicorn
uvicorn src.chatbot_service:app --host 0.0.0.0 --port 8000 &

# Docker:
docker restart chatbot-service

# ECS:
aws ecs update-service \
  --cluster chatbot-cluster \
  --service chatbot-service \
  --force-new-deployment

# 4. Verify restart
sleep 10
curl http://localhost:8000/health
```

**Investigation (2-10 minutes):**
```bash
# Check for OOM kills
dmesg | grep -i "out of memory"
docker inspect chatbot-service | grep OOMKilled

# Check disk space
df -h

# Check dependencies
python scripts/check_dependencies.py

# Check environment variables
docker exec chatbot-service env | grep -E "OPENAI|VECTOR_STORE"

# Check recent deployments
git log --oneline --since="1 day ago"
```

**Mitigation:**
```bash
# If OOM, increase memory
# Update task definition (ECS)
vim task-definition.json  # Increase memory to 2048
aws ecs register-task-definition --cli-input-json file://task-definition.json

# If dependency issue, rebuild
docker build --no-cache -t chatbot-service:v1.1 .
docker run -d -p 8000:8000 chatbot-service:v1.1

# If configuration issue, fix and redeploy
vim .env
docker-compose up -d --build
```

#### P0: Vector Store Unreachable

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check vector store connectivity
curl -XGET "https://search-domain.us-east-1.es.amazonaws.com/_cluster/health"

# For Pinecone:
curl -X GET "https://api.pinecone.io/indexes/knowledge-base/describe" \
  -H "Api-Key: $PINECONE_API_KEY"

# 2. Check network connectivity
ping search-domain.us-east-1.es.amazonaws.com
telnet search-domain.us-east-1.es.amazonaws.com 443

# 3. Check credentials
echo $VECTOR_STORE_URL
echo $VECTOR_STORE_API_KEY | head -c 20

# 4. Enable fallback mode (if available)
export ENABLE_FALLBACK_SEARCH=true
kubectl set env deployment/chatbot-service ENABLE_FALLBACK_SEARCH=true -n chatbot
```

**Investigation:**
```bash
# Check OpenSearch cluster status
aws opensearch describe-domain --domain-name chatbot-search

# Check recent changes
aws opensearch describe-domain-config --domain-name chatbot-search

# Check security groups
aws ec2 describe-security-groups --group-ids sg-...

# Review access policies
aws opensearch describe-domain --domain-name chatbot-search --query 'DomainStatus.AccessPolicies'
```

**Mitigation:**
```bash
# If cluster unhealthy, restart
aws opensearch reboot-domain --domain-name chatbot-search

# If access issue, update policy
cat > policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::123456789:role/ChatbotServiceRole"},
    "Action": "es:*",
    "Resource": "arn:aws:es:us-east-1:123456789:domain/chatbot-search/*"
  }]
}
EOF

aws opensearch update-domain-config \
  --domain-name chatbot-search \
  --access-policies file://policy.json

# If complete failure, failover to backup
export VECTOR_STORE_URL="https://backup-search-domain.us-west-2.es.amazonaws.com"
kubectl set env deployment/chatbot-service VECTOR_STORE_URL=$VECTOR_STORE_URL -n chatbot
```

#### P1: High LLM Error Rate

**Investigation:**
```bash
# Check OpenAI API status
curl https://status.openai.com/api/v2/status.json

# Review error logs
grep "LLM error" logs/chatbot.log | tail -50

# Check rate limits
python scripts/check_rate_limits.py

# Test direct API call
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

**Mitigation:**
```bash
# Option 1: Implement retry with exponential backoff
export LLM_MAX_RETRIES=3
export LLM_RETRY_DELAY=2
kubectl set env deployment/chatbot-service LLM_MAX_RETRIES=3 LLM_RETRY_DELAY=2 -n chatbot

# Option 2: Switch to backup provider
export LLM_PROVIDER="azure"
export AZURE_OPENAI_ENDPOINT="https://backup.openai.azure.com/"
kubectl set env deployment/chatbot-service \
  LLM_PROVIDER=azure \
  AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
  -n chatbot

# Option 3: Reduce request rate
export LLM_RATE_LIMIT=10  # requests per second
kubectl set env deployment/chatbot-service LLM_RATE_LIMIT=10 -n chatbot

# Option 4: Enable request queuing
python scripts/enable_request_queue.py --max-queue-size 1000
```

#### P1: High Response Latency

**Investigation:**
```bash
# Profile request
python scripts/profile_request.py --query "How do I deploy a model?"

# Expected output:
# Total time: 8.5s
#   Vector search: 0.15s
#   LLM generation: 7.8s
#   Tool execution: 0.35s
#   Other: 0.2s

# Check vector store latency
python scripts/benchmark_vector_search.py --iterations 100

# Check LLM latency
python scripts/benchmark_llm.py --iterations 50

# Check system resources
docker stats chatbot-service
# or
aws ecs describe-tasks --cluster chatbot-cluster --tasks $TASK_ARN
```

**Mitigation:**
```bash
# If vector search slow, optimize queries
python scripts/optimize_search_params.py

# If LLM slow, reduce context size
export MAX_CONTEXT_LENGTH=2000  # tokens
kubectl set env deployment/chatbot-service MAX_CONTEXT_LENGTH=2000 -n chatbot

# If resource constrained, scale up
aws ecs update-service \
  --cluster chatbot-cluster \
  --service chatbot-service \
  --desired-count 5

# Enable caching for common queries
export ENABLE_RESPONSE_CACHE=true
export CACHE_TTL=3600
kubectl set env deployment/chatbot-service \
  ENABLE_RESPONSE_CACHE=true \
  CACHE_TTL=3600 \
  -n chatbot
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** 35 minutes
**Affected Component:** LLM integration

## Timeline
- 15:00: High error rate detected (15% LLM failures)
- 15:05: Confirmed OpenAI API rate limit hit
- 15:10: Enabled request queuing
- 15:15: Reduced request rate to 10/s
- 15:25: Error rate returned to normal (< 1%)
- 15:35: Full recovery confirmed

## Root Cause
Unexpected traffic spike exceeded OpenAI rate limits

## Action Items
- [ ] Implement adaptive rate limiting
- [ ] Set up multi-provider failover
- [ ] Add request queue monitoring
- [ ] Increase OpenAI rate limits with provider

EOF

# Review metrics during incident
python scripts/generate_incident_report.py \
  --start "2025-11-10T15:00:00" \
  --end "2025-11-10T15:35:00" \
  > incidents/metrics-$(date +%Y%m%d-%H%M).html
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: "Context Length Exceeded"

**Symptoms:**
```
Error: This model's maximum context length is 8192 tokens
```

**Diagnosis:**
```bash
# Check context size
python scripts/analyze_context_size.py --conversation-id "abc123"

# Example output:
# Conversation: abc123
# Messages: 15
# Total tokens: 9500
#   System prompt: 500
#   Conversation history: 3000
#   Retrieved context: 5500
#   Current query: 500
```

**Solution:**
```bash
# Reduce context window
export MAX_CONTEXT_LENGTH=4000
export MAX_HISTORY_MESSAGES=5
kubectl set env deployment/chatbot-service \
  MAX_CONTEXT_LENGTH=4000 \
  MAX_HISTORY_MESSAGES=5 \
  -n chatbot

# Or implement sliding window
python scripts/enable_sliding_window.py --window-size 10

# Or use a model with larger context
export LLM_MODEL="gpt-4-32k"
kubectl set env deployment/chatbot-service LLM_MODEL=gpt-4-32k -n chatbot
```

---

#### Issue: Low Context Relevance

**Symptoms:**
- Chatbot provides irrelevant answers
- Users report poor response quality

**Diagnosis:**
```bash
# Evaluate search quality
python scripts/evaluate_search.py --test-queries test/queries.json

# Example output:
# Average relevance score: 0.52
# Top-1 accuracy: 45%
# Top-5 accuracy: 68%

# Analyze embeddings
python scripts/analyze_embeddings.py --sample-size 100
```

**Solution:**
```bash
# Option 1: Retune search parameters
python scripts/tune_search_params.py \
  --metric relevance \
  --optimization-trials 50

# Option 2: Upgrade embedding model
export EMBEDDING_MODEL="text-embedding-3-large"
python scripts/reindex_with_new_embeddings.py

# Option 3: Add metadata filtering
python scripts/add_metadata_filters.py --config filters.yaml

# Option 4: Implement hybrid search
python scripts/enable_hybrid_search.py --bm25-weight 0.3 --vector-weight 0.7
```

---

## Maintenance Procedures

### Daily Tasks

```bash
# Morning health check
curl http://localhost:8000/health
python scripts/daily_health_check.py

# Check service logs for errors
tail -100 logs/chatbot.log | grep -i error

# Monitor token usage
python scripts/get_token_usage.py --date $(date +%Y-%m-%d)

# Check conversation metrics
python scripts/conversation_metrics.py --date $(date +%Y-%m-%d)
```

### Weekly Tasks

```bash
# Review response quality
python scripts/quality_report.py --days 7

# Clean up old conversations
python scripts/archive_conversations.py --older-than 30

# Update vector store index
python scripts/incremental_index_update.py --source data/knowledge_base/

# Review and optimize prompts
python scripts/analyze_prompts.py --days 7
```

### Monthly Tasks

```bash
# Comprehensive system audit
python scripts/system_audit.py --report monthly-$(date +%Y-%m).html

# Review and update knowledge base
git pull knowledge-base-repo
python scripts/rebuild_index.py

# Update embedding model if available
python scripts/check_model_updates.py
# If updates available:
python scripts/migrate_to_new_embedding_model.py

# Review cost and optimize
python scripts/cost_analysis.py --month $(date +%Y-%m)
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective):
  - Conversations: 5 minutes (database backup)
  - Vector index: 1 hour (snapshot interval)
  - Service code: 0 (version controlled)

- **RTO** (Recovery Time Objective):
  - Service: 5 minutes (container restart)
  - Vector store: 15 minutes (restore from snapshot)
  - Full system: 30 minutes (complete redeployment)

### Backup Strategy

```bash
# Daily automated backups
cat > scripts/daily_backup.sh << 'EOF'
#!/bin/bash

# Backup conversation database
pg_dump chatbot_db > backups/chatbot-db-$(date +%Y%m%d).sql

# Backup vector store
curl -XPUT "https://search-domain/_snapshot/daily/snapshot_$(date +%Y%m%d)"

# Backup configurations
kubectl get configmap chatbot-config -n chatbot -o yaml > backups/config-$(date +%Y%m%d).yaml

echo "Backup completed at $(date)"
EOF

chmod +x scripts/daily_backup.sh
```

### Disaster Recovery Procedures

**Complete Service Loss (30 minutes):**
```bash
# 1. Redeploy service
docker-compose up -d
# or
kubectl apply -f k8s/

# 2. Restore database
psql chatbot_db < backups/chatbot-db-latest.sql

# 3. Restore vector store
curl -XPOST "https://search-domain/_snapshot/daily/snapshot_latest/_restore"

# 4. Verify recovery
curl http://localhost:8000/health
python scripts/smoke_test.py
```

---

## Quick Reference Card

### Most Common Operations

```bash
# Start service
uvicorn src.chatbot_service:app --host 0.0.0.0 --port 8000

# Test chat
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"message": "Hello"}'

# Index documents
python scripts/index_documents.py --source data/knowledge_base/

# Check health
curl http://localhost:8000/health

# View logs
tail -f logs/chatbot.log

# Deploy to ECS
docker build -t chatbot:v1 . && docker push <ecr>/chatbot:v1 && aws ecs update-service --force-new-deployment
```

### Emergency Response

```bash
# P0: Service down
docker restart chatbot-service

# P0: Vector store down
aws opensearch reboot-domain --domain-name chatbot-search

# P1: LLM errors
export LLM_PROVIDER=azure && kubectl set env deployment/chatbot-service LLM_PROVIDER=azure

# P1: High latency
aws ecs update-service --cluster chatbot-cluster --service chatbot-service --desired-count 5
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** AI Platform Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates
