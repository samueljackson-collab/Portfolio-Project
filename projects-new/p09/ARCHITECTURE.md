# P09 Architecture Diagrams

## End-to-End RAG Flow
```mermaid
graph LR
    subgraph Sources
      DOCS[Documents: PDF/MD/HTML]
    end
    subgraph Ingestion
      FETCH[Fetch Documents]
      CHUNK[Chunking + Overlap]
      EMBED[Generate Embeddings]
    end
    subgraph Storage
      VDB[(Vector Database)]
    end
    subgraph Query
      USER[User Query]
      SEARCH[Hybrid Search]
      RERANK[Reranking]
      GEN[LLM Generation]
    end
    DOCS --> FETCH
    FETCH --> CHUNK
    CHUNK --> EMBED
    EMBED --> VDB
    USER --> SEARCH
    SEARCH --> VDB
    VDB --> RERANK
    RERANK --> GEN
    GEN --> USER
```
**Explanation:** Documents are fetched, chunked with overlap, and embedded using sentence-transformers or OpenAI. Vectors are stored in a database (Pinecone/pgvector/Weaviate). When users query, hybrid search (semantic + keyword) retrieves candidates, cross-encoder reranks them, and the LLM generates a grounded response using the top-k contexts.

## Component View
```mermaid
graph TB
    subgraph API
      FASTAPI[FastAPI Server]
      AUTH[Auth Middleware]
      RATE[Rate Limiter]
    end
    subgraph Backend
      RET[Retrieval Service]
      GEN[Generation Service]
      CACHE[Redis Cache]
    end
    subgraph Workers
      ING[Ingestion Worker]
      QUEUE[Task Queue]
    end
    subgraph Data
      VDB[(Vector DB)]
      LOGS[(Logs + Metrics)]
    end
    subgraph External
      LLM[LLM API: OpenAI/Anthropic]
      DOCS[Document Sources]
    end
    FASTAPI --> AUTH
    AUTH --> RATE
    RATE --> RET
    RET --> VDB
    RET --> CACHE
    RET --> GEN
    GEN --> LLM
    ING --> QUEUE
    QUEUE --> VDB
    DOCS --> ING
    FASTAPI --> LOGS
```
**Explanation:** FastAPI handles incoming requests through auth and rate limiting middleware. Retrieval service queries the vector DB and cache for relevant context. Generation service calls LLM with retrieved context. Ingestion workers run asynchronously, processing documents from queue. All interactions are logged for observability.

## Scaling Path
```mermaid
graph LR
    subgraph LoadBalancer
      LB[AWS ALB / NGINX]
    end
    subgraph APIWorkers
      W1[FastAPI Worker 1]
      W2[FastAPI Worker 2]
      W3[FastAPI Worker N]
    end
    subgraph VectorDB
      VDB1[Shard 1]
      VDB2[Shard 2]
      VDB3[Shard N]
    end
    subgraph Cache
      REDIS[Redis Cluster]
    end
    LB --> W1
    LB --> W2
    LB --> W3
    W1 --> REDIS
    W2 --> REDIS
    W3 --> REDIS
    W1 --> VDB1
    W1 --> VDB2
    W2 --> VDB2
    W2 --> VDB3
    W3 --> VDB1
```
**Explanation:** Load balancer distributes traffic across multiple FastAPI workers. Vector database is sharded for horizontal scaling. Redis cluster provides distributed caching for frequently accessed embeddings and responses. Auto-scaling groups adjust worker count based on request rate.

## Fallback & Guardrails
```mermaid
graph TD
    QUERY[User Query]
    VALIDATE[Input Validation]
    PII[PII Detection]
    RETRIEVE[Retrieval]
    CHECK[Relevance Check]
    GENERATE[Generation]
    FILTER[Output Filter]
    RESPONSE[Response]
    FALLBACK[Fallback Response]

    QUERY --> VALIDATE
    VALIDATE -->|Invalid| FALLBACK
    VALIDATE -->|Valid| PII
    PII -->|PII Detected| FALLBACK
    PII -->|Clean| RETRIEVE
    RETRIEVE --> CHECK
    CHECK -->|Low Relevance| FALLBACK
    CHECK -->|Relevant| GENERATE
    GENERATE --> FILTER
    FILTER -->|Unsafe| FALLBACK
    FILTER -->|Safe| RESPONSE
```
**Explanation:** Multiple safety checks guard against bad inputs and outputs. Input validation catches malformed queries, PII detection blocks sensitive data, relevance check ensures retrieved context is useful, and output filter scans for hallucinations or unsafe content. Fallback responses handle edge cases gracefully.
