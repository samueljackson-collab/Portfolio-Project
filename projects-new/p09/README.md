# P09 — Advanced AI Chatbot with Retrieval-Augmented Generation (RAG)

**Tagline:** Enterprise knowledge assistant with FastAPI backend, vector database retrieval, and LLM generation for grounded, low-hallucination responses.

## Executive Summary
- **Grounded Answers:** RAG architecture retrieves relevant context from proprietary documents before generating responses, dramatically reducing hallucination rates
- **Scalable Backend:** FastAPI with async workers, rate limiting, and authentication supports production traffic
- **Flexible Vector Store:** Supports multiple backends (Pinecone, pgvector, Weaviate) for semantic search
- **Continuous Improvement:** Feedback loops, eval harnesses, and drift detection ensure quality over time
- **Enterprise Controls:** PII redaction, audit logging, prompt injection defense, and cost tracking

## Architecture Overview

### End-to-End RAG Flow
**Documents** → **Ingestion Pipeline** (chunking/embedding) → **Vector DB** → **Query Flow** (retrieve/rerank/generate) → **User Response**

### Components
- **FastAPI Backend:** REST API with `/chat` endpoint, JWT auth, rate limiting, request/response logging
- **Ingestion Pipeline:** Async worker fetching docs, chunking with overlap, generating embeddings (sentence-transformers or OpenAI), upserting to vector DB
- **Vector Database:** Pinecone/pgvector/Weaviate for semantic search with metadata filtering
- **Retrieval Module:** Hybrid search (semantic + keyword), reranking (cross-encoder), grounding score calculation
- **Generation Module:** LLM orchestration (OpenAI/Anthropic/local), prompt templating, streaming responses, fallback logic
- **Observability:** OpenTelemetry tracing, Prometheus metrics (latency, token usage, cost), structured logging with PII redaction

### Directory Layout
```
projects-new/p09/
├── README.md
├── ARCHITECTURE.md
├── TESTING.md
├── REPORT_TEMPLATES.md
├── PLAYBOOK.md
├── RUNBOOKS.md
├── SOP.md
├── METRICS.md
├── ADRS.md
├── THREAT_MODEL.md
├── RISK_REGISTER.md
├── app/
│   ├── main.py               # FastAPI application
│   ├── ingestion.py          # Document chunking and embedding
│   ├── retrieval.py          # Hybrid search and reranking
│   ├── generation.py         # LLM prompting and streaming
│   ├── auth.py               # JWT/API key authentication
│   └── config.py             # Environment configuration
├── tests/
│   ├── test_retrieval.py
│   ├── test_generation.py
│   └── eval_harness.py       # Grounding/quality evaluation
└── docker-compose.yml
```

## Setup

### Prerequisites
- Python 3.10+
- Vector database (Pinecone account or local pgvector/Weaviate)
- OpenAI/Anthropic API key or local LLM (Ollama)
- Docker for local development

### Installation
```bash
cd projects-new/p09
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export VECTOR_DB_URL="postgresql://user:pass@localhost:5432/vectors"
export OPENAI_API_KEY="sk-..."
export JWT_SECRET="your-secret"
```

### Run Locally
```bash
# Start vector DB (if using pgvector)
docker-compose up -d postgres

# Run ingestion (one-time or scheduled)
python -m app.ingestion --docs-path ./knowledge_base/

# Start API server
uvicorn app.main:app --reload --port 8000
```

### Query Example
```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is our refund policy?", "stream": false}'
```

## Data Flow
1. **Document Acquisition:** Fetch from S3/SharePoint/Confluence via connectors
2. **Chunking:** Split into overlapping chunks (512 tokens, 50 token overlap)
3. **Embedding:** Generate vectors with sentence-transformers or OpenAI `text-embedding-ada-002`
4. **Upsert:** Store in vector DB with metadata (source, timestamp, version)
5. **Query:** User submits question via `/chat` endpoint
6. **Retrieval:** Hybrid search returns top-k chunks (semantic + BM25 fusion)
7. **Reranking:** Cross-encoder scores relevance; select top-3
8. **Generation:** LLM receives prompt with context chunks; generates grounded answer
9. **Response:** Stream or return complete response with citations
10. **Feedback:** User thumbs-up/down captured for eval dataset

## Evaluation
- **Grounding Score:** % of responses with citations; flagged hallucinations
- **Recall@k:** Relevant docs in top-k retrievals (measured on labeled test set)
- **Latency:** p95 retrieval + generation time
- **User Feedback:** Thumbs-up rate, flagged responses
- **Regression Harness:** Suite of 100+ prompts with expected answers; run pre-deploy

## Observability
- **Tracing (OpenTelemetry):** Span per retrieval, rerank, generation step; visualize in Jaeger
- **Metrics (Prometheus):** Latency histograms, error rates, token usage, cost per request
- **Logging:** Structured JSON logs with trace IDs; PII redacted via regex filters
- **Cost Control:** Token usage tracked per user; budget alerts; rate limiting per API key

## Security
- **Authentication:** JWT tokens or API keys; RBAC for admin endpoints
- **Rate Limiting:** 100 requests/minute per user; burst allowance
- **PII Handling:** Detect and redact SSN/credit cards in queries and logs
- **Prompt Injection Defense:** Input sanitization, output filtering, sandboxed LLM calls
- **Audit Logging:** All queries logged with user ID, timestamp, response for compliance

## Hiring Manager Highlights
- **Applied AI:** Demonstrates RAG implementation with retrieval, reranking, and generation pipeline
- **Backend Engineering:** Production-grade FastAPI with async, auth, rate limiting, and observability
- **Reliability:** Includes eval harnesses, drift detection, fallback logic, and operational runbooks
- **Security-Minded:** PII redaction, prompt injection defense, and audit logging show enterprise awareness
