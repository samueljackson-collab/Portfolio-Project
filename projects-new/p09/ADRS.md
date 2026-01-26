# Architecture Decision Records

## ADR-001: Vector Database Choice (Pinecone vs pgvector vs Weaviate)
- **Context:** Need scalable vector storage with semantic search for millions of documents
- **Decision:** Use pgvector with PostgreSQL for self-hosted control and cost efficiency
- **Alternatives:** Pinecone (managed, expensive at scale), Weaviate (feature-rich, more complex), FAISS (no persistence)
- **Pros:** SQL familiarity, ACID guarantees, cost control, hybrid search with PostgreSQL full-text
- **Cons:** Requires database management, scaling needs sharding strategy
- **Consequences:** Deploy Postgres with pgvector extension; implement sharding for >10M vectors
- **Revisit:** If operational burden too high or need managed solution

## ADR-002: Embedding Model Selection
- **Context:** Need balance between quality, latency, and cost for document embedding
- **Decision:** Use sentence-transformers `all-MiniLM-L6-v2` for local embedding
- **Alternatives:** OpenAI `text-embedding-ada-002` (high quality, API cost), larger models (better quality, slower)
- **Pros:** Fast inference, no API costs, 384-dim vectors (storage efficient), good recall for general domains
- **Cons:** Lower quality than OpenAI for complex queries
- **Consequences:** Self-host embedding service; monitor recall metrics; upgrade if insufficient
- **Revisit:** If recall < 80% on eval set

## ADR-003: Retrieval Strategy (Semantic vs Keyword vs Hybrid)
- **Context:** Pure semantic search misses exact matches; pure keyword misses synonyms
- **Decision:** Implement hybrid search with 70% semantic, 30% keyword (BM25) weight
- **Alternatives:** Semantic-only, keyword-only, learned fusion weights
- **Pros:** Best of both worlds, handles exact and conceptual matches
- **Cons:** Increased complexity, two index paths
- **Consequences:** Maintain both vector and full-text indexes; tune weights based on query types
- **Revisit:** If user feedback shows poor relevance

## ADR-004: LLM Provider Choice
- **Context:** Need reliable, cost-effective LLM for response generation
- **Decision:** Use OpenAI GPT-3.5-turbo with fallback to GPT-4 for complex queries
- **Alternatives:** Anthropic Claude (higher quality, more expensive), local models (Llama, lower quality), GPT-4 only (expensive)
- **Pros:** Good quality/cost balance, fast response, wide context window
- **Cons:** API dependency, token costs at scale
- **Consequences:** Implement token tracking and budgets; evaluate Claude for critical use cases
- **Revisit:** If cost >$X/month or latency >2s p95

## ADR-005: Caching Strategy
- **Context:** Repeated queries waste tokens and increase latency
- **Decision:** Implement Redis caching for embeddings and responses with 1-hour TTL
- **Alternatives:** No caching, longer TTL, CDN caching for static content
- **Pros:** Reduces LLM calls by ~40%, improves latency for common queries
- **Cons:** Cache invalidation complexity, stale responses
- **Consequences:** Deploy Redis cluster; implement cache warming for FAQs; monitor hit rate
- **Revisit:** If cache hit rate < 30%

## ADR-006: Safety & Guardrail Approach
- **Context:** Need to prevent prompt injection, PII leakage, and hallucinations
- **Decision:** Multi-layer defense: input validation, PII detection (regex + NER), output filtering, human review for flagged responses
- **Alternatives:** LLM-based moderation only, no guardrails (risky), WAF-only (insufficient)
- **Pros:** Defense in depth, catches multiple attack vectors
- **Cons:** Adds latency (~50ms), false positives possible
- **Consequences:** Implement guardrail pipeline; log all filtered requests; tune thresholds monthly
- **Revisit:** If false positive rate > 5%

## ADR-007: Deployment Model (Serverless vs Container)
- **Context:** Need scalable, cost-effective hosting for FastAPI application
- **Decision:** Deploy on Kubernetes with HPA, keep functions stateless
- **Alternatives:** AWS Lambda (cold start issues for ML models), EC2 (less elastic)
- **Pros:** Predictable latency, easy GPU integration for local models, auto-scaling
- **Cons:** Requires cluster management, baseline cost for nodes
- **Consequences:** Containerize with Docker; deploy to EKS/GKE with spot instances
- **Revisit:** If traffic <1000 req/day (consider serverless)
