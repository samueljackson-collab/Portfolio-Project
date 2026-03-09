# P09 Testing Strategy (RAG Chatbot)

## Strategy Overview
- **Ingestion Quality:** Validate chunking, embedding correctness, vector DB upserts
- **Retrieval Accuracy:** Measure recall@k, precision, reranking effectiveness
- **Generation Quality:** Assess grounding score, hallucination rate, response relevance
- **Evaluation Harness:** Automated testing with labeled Q&A dataset
- **Security Testing:** Prompt injection, PII leakage, auth bypass attempts
- **Performance Testing:** Latency under load, cost per request, token usage
- **CI Stages:** Per-commit unit tests, nightly eval runs, staging deployment tests

## Test Matrix
| ID | Category | Description | Preconditions | Steps | Expected | Tools |
|----|----------|-------------|---------------|-------|----------|-------|
| T01 | Ingestion | Chunking produces correct overlap | Test doc with 1000 tokens | Chunk with 512 size, 50 overlap | 3 chunks with expected boundaries | pytest |
| T02 | Ingestion | Embeddings have correct dimensions | Text chunks ready | Generate embeddings | 384-dim vectors (MiniLM) or 1536 (OpenAI) | pytest, numpy |
| T03 | Ingestion | Duplicate documents handled | Upload same doc twice | Check vector DB | Only one set of chunks stored (by hash) | pytest |
| T04 | Retrieval | Semantic search returns relevant docs | Populated vector DB | Query "refund policy" | Top-3 contain refund docs | pytest |
| T05 | Retrieval | Hybrid search outperforms semantic-only | Test queries with exact matches | Compare hybrid vs semantic | Hybrid recall@5 > semantic by 10% | eval_harness.py |
| T06 | Retrieval | Reranking improves top-3 relevance | Semantic candidates | Apply cross-encoder | Reranked top-3 precision > 90% | pytest |
| T07 | Generation | Response includes citations | Context + query | Generate answer | Answer contains [1], [2] references | pytest |
| T08 | Generation | Grounding score high for cited answers | Generated response | Compute grounding | Score = 1.0 if citations present | pytest |
| T09 | Generation | Hallucination detection | Query with no relevant context | Generate | Response says "insufficient information" | eval_harness.py |
| T10 | Evaluation | Regression harness detects quality drop | Baseline model | Run 100 test queries | <5% accuracy drop vs baseline | eval_harness.py |
| T11 | Security | Prompt injection blocked | Malicious query with "ignore instructions" | Send to API | Sanitized or rejected | pytest, OWASP Zap |
| T12 | Security | PII redaction in logs | Query with SSN | Check logs | SSN redacted | pytest |
| T13 | Security | Auth enforcement | Request without token | Call /chat | 401 Unauthorized | pytest |
| T14 | Security | Rate limiting works | Burst 200 requests | Hit API | Requests >100/min throttled | locust |
| T15 | Performance | Latency p95 < 2s | Load test with 10 RPS | Measure response time | p95 latency < 2000ms | locust, prometheus |
| T16 | Performance | Cost per request tracked | 100 queries | Check metrics | Cost logged, <$0.01/request | pytest, cost tracking |
| T17 | Performance | Streaming reduces perceived latency | Enable stream mode | Measure TTFB | First token < 500ms | pytest |
| T18 | Reliability | Vector DB outage handled | Stop vector DB | Query API | Graceful error, fallback response | pytest |
| T19 | Reliability | LLM API failure retry | Mock API error | Generate | Retries 3x with backoff | pytest |
| T20 | User Experience | Feedback capture works | Submit thumbs down | Check DB | Feedback logged with query ID | pytest |

## Evaluation Harness
```python
# eval_harness.py structure
class EvalHarness:
    def load_test_set(self):
        # Load labeled Q&A pairs with expected sources
        pass

    def evaluate_retrieval(self):
        # Measure recall@k, precision@k, MRR
        pass

    def evaluate_generation(self):
        # Measure grounding score, hallucination rate, ROUGE/BLEU
        pass

    def compare_to_baseline(self):
        # Detect regressions
        pass
```

## CI Integration
```yaml
# .github/workflows/test.yml
- name: Unit Tests
  run: pytest tests/ -v

- name: Eval Harness
  run: python tests/eval_harness.py --dataset test_set.json

- name: Security Scan
  run: bandit -r app/

- name: Load Test
  run: locust -f tests/load_test.py --headless -u 50 -r 10 --run-time 2m
```

## Performance Benchmarks
- **Ingestion:** 1000 docs/hour on single worker
- **Retrieval:** 100 QPS with <100ms latency (cached)
- **Generation:** p95 < 2s end-to-end (non-streaming)
- **Cost:** <$0.005 per request (GPT-3.5 tokens)
