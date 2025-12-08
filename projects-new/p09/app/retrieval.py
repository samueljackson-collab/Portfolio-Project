"""Retrieval module with hybrid search and reranking."""
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder

class RetrievalService:
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        self.embedding_model = SentenceTransformer(embedding_model)
        self.rerank_model = CrossEncoder(rerank_model)

    async def semantic_search(
        self,
        query: str,
        vector_db_client,
        top_k: int = 10,
        collection_name: str = "knowledge_base"
    ) -> List[Dict]:
        """Semantic similarity search using embeddings."""
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()

        # Search vector DB
        results = await vector_db_client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=top_k
        )

        return results

    async def keyword_search(
        self,
        query: str,
        vector_db_client,
        top_k: int = 10
    ) -> List[Dict]:
        """Keyword-based BM25 search (if supported by vector DB)."""
        # Fallback: use metadata filtering or full-text search
        results = await vector_db_client.keyword_search(
            query=query,
            limit=top_k
        )
        return results

    async def hybrid_search(
        self,
        query: str,
        vector_db_client,
        top_k: int = 10,
        semantic_weight: float = 0.7
    ) -> List[Dict]:
        """Combine semantic and keyword search with weighted fusion."""
        # Get both result sets
        semantic_results = await self.semantic_search(query, vector_db_client, top_k * 2)
        keyword_results = await self.keyword_search(query, vector_db_client, top_k * 2)

        # Score fusion (Reciprocal Rank Fusion)
        scores = {}
        for rank, result in enumerate(semantic_results):
            doc_id = result['id']
            scores[doc_id] = scores.get(doc_id, 0) + semantic_weight / (rank + 1)

        for rank, result in enumerate(keyword_results):
            doc_id = result['id']
            scores[doc_id] = scores.get(doc_id, 0) + (1 - semantic_weight) / (rank + 1)

        # Sort by fused score
        ranked_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:top_k]

        # Retrieve full documents
        all_results = {r['id']: r for r in semantic_results + keyword_results}
        hybrid_results = [all_results[doc_id] for doc_id in ranked_ids if doc_id in all_results]

        return hybrid_results

    async def rerank(
        self,
        query: str,
        candidates: List[Dict],
        top_k: int = 3
    ) -> List[Dict]:
        """Rerank candidates using cross-encoder for better relevance."""
        if not candidates:
            return []

        # Prepare pairs
        pairs = [(query, c['text']) for c in candidates]

        # Score with cross-encoder
        scores = self.rerank_model.predict(pairs)

        # Sort by score
        ranked_indices = np.argsort(scores)[::-1][:top_k]

        # Add rerank scores to results
        reranked = []
        for idx in ranked_indices:
            result = candidates[idx].copy()
            result['rerank_score'] = float(scores[idx])
            reranked.append(result)

        return reranked

    def compute_grounding_score(
        self,
        answer: str,
        sources: List[Dict]
    ) -> float:
        """Compute grounding score based on citation presence."""
        # Simple heuristic: check for source references in answer
        has_citation = any(
            source['metadata']['source'] in answer or
            f"[{i+1}]" in answer
            for i, source in enumerate(sources)
        )

        # Could enhance with NLI model for entailment checking
        return 1.0 if has_citation else 0.5


async def hybrid_search(query: str, top_k: int = 5) -> List[Dict]:
    """Convenience wrapper for FastAPI endpoint."""
    # Initialize service (would typically be dependency injection)
    service = RetrievalService()
    # Assume vector_db_client is initialized elsewhere
    from .config import get_vector_db_client
    client = get_vector_db_client()

    results = await service.hybrid_search(query, client, top_k)
    return results


async def rerank(query: str, candidates: List[Dict]) -> List[Dict]:
    """Convenience wrapper for reranking."""
    service = RetrievalService()
    reranked = await service.rerank(query, candidates)
    return reranked
