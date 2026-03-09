#!/usr/bin/env python3
"""
Vector Store Implementations

Supports multiple vector database backends:
- OpenSearch
- Pinecone
- ChromaDB
- In-memory (for development/testing)
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import httpx

from config import VectorStoreConfig, VectorStoreProvider

logger = logging.getLogger("vector-store")


@dataclass
class Document:
    """A document with content and metadata."""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None
    score: float = 0.0

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseVectorStore(ABC):
    """Abstract base class for vector stores."""

    def __init__(self, config: VectorStoreConfig):
        self.config = config

    @abstractmethod
    async def index(self, documents: List[Document]) -> bool:
        """Index documents into the store."""
        pass

    @abstractmethod
    async def search(self, query_embedding: List[float], limit: int = 5,
                    filters: Optional[Dict] = None) -> List[Document]:
        """Search for similar documents."""
        pass

    @abstractmethod
    async def delete(self, document_ids: List[str]) -> bool:
        """Delete documents by ID."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the store is healthy."""
        pass


class OpenSearchVectorStore(BaseVectorStore):
    """OpenSearch vector store implementation."""

    def __init__(self, config: VectorStoreConfig):
        super().__init__(config)
        protocol = "https" if config.use_ssl else "http"
        self.base_url = f"{protocol}://{config.host}:{config.port}"
        self.index_name = config.index_name

        auth = None
        if config.api_key:
            # Basic auth format: username:password
            auth = tuple(config.api_key.split(":")) if ":" in config.api_key else None

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            auth=auth,
            verify=config.verify_certs,
            timeout=30.0
        )

    async def _ensure_index(self):
        """Create index if it doesn't exist."""
        try:
            response = await self.client.head(f"/{self.index_name}")
            if response.status_code == 404:
                # Create index with vector mapping
                mapping = {
                    "settings": {
                        "index": {
                            "knn": True,
                            "knn.algo_param.ef_search": 100
                        }
                    },
                    "mappings": {
                        "properties": {
                            "content": {"type": "text"},
                            "embedding": {
                                "type": "knn_vector",
                                "dimension": self.config.embedding_dimensions,
                                "method": {
                                    "name": "hnsw",
                                    "space_type": "cosinesimil",
                                    "engine": "nmslib",
                                    "parameters": {
                                        "ef_construction": 128,
                                        "m": 24
                                    }
                                }
                            },
                            "metadata": {"type": "object", "enabled": True}
                        }
                    }
                }
                await self.client.put(f"/{self.index_name}", json=mapping)
                logger.info(f"Created OpenSearch index: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to ensure index: {e}")

    async def index(self, documents: List[Document]) -> bool:
        """Index documents into OpenSearch."""
        await self._ensure_index()

        bulk_body = []
        for doc in documents:
            bulk_body.append(json.dumps({"index": {"_index": self.index_name, "_id": doc.id}}))
            bulk_body.append(json.dumps({
                "content": doc.content,
                "embedding": doc.embedding,
                "metadata": doc.metadata
            }))

        response = await self.client.post(
            "/_bulk",
            content="\n".join(bulk_body) + "\n",
            headers={"Content-Type": "application/x-ndjson"}
        )
        return response.status_code == 200

    async def search(self, query_embedding: List[float], limit: int = 5,
                    filters: Optional[Dict] = None) -> List[Document]:
        """Search for similar documents using k-NN."""
        query = {
            "size": limit,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": limit
                    }
                }
            }
        }

        if filters:
            query["query"] = {
                "bool": {
                    "must": [query["query"]],
                    "filter": [{"term": {f"metadata.{k}": v}} for k, v in filters.items()]
                }
            }

        response = await self.client.post(
            f"/{self.index_name}/_search",
            json=query
        )
        response.raise_for_status()
        data = response.json()

        documents = []
        for hit in data.get("hits", {}).get("hits", []):
            source = hit["_source"]
            documents.append(Document(
                id=hit["_id"],
                content=source["content"],
                embedding=source.get("embedding"),
                metadata=source.get("metadata", {}),
                score=hit["_score"]
            ))

        return documents

    async def delete(self, document_ids: List[str]) -> bool:
        """Delete documents by ID."""
        bulk_body = []
        for doc_id in document_ids:
            bulk_body.append(json.dumps({"delete": {"_index": self.index_name, "_id": doc_id}}))

        response = await self.client.post(
            "/_bulk",
            content="\n".join(bulk_body) + "\n",
            headers={"Content-Type": "application/x-ndjson"}
        )
        return response.status_code == 200

    async def health_check(self) -> bool:
        """Check OpenSearch cluster health."""
        try:
            response = await self.client.get("/_cluster/health")
            return response.status_code == 200
        except Exception:
            return False


class PineconeVectorStore(BaseVectorStore):
    """Pinecone vector store implementation."""

    def __init__(self, config: VectorStoreConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.index_name = config.index_name
        self.host = config.host  # Pinecone index URL

        self.client = httpx.AsyncClient(
            base_url=f"https://{self.host}",
            headers={"Api-Key": self.api_key},
            timeout=30.0
        )

    async def index(self, documents: List[Document]) -> bool:
        """Index documents into Pinecone."""
        vectors = []
        for doc in documents:
            vectors.append({
                "id": doc.id,
                "values": doc.embedding,
                "metadata": {
                    "content": doc.content[:1000],  # Pinecone metadata limit
                    **doc.metadata
                }
            })

        # Batch upsert (max 100 per request)
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            response = await self.client.post(
                "/vectors/upsert",
                json={"vectors": batch, "namespace": "default"}
            )
            if response.status_code != 200:
                return False

        return True

    async def search(self, query_embedding: List[float], limit: int = 5,
                    filters: Optional[Dict] = None) -> List[Document]:
        """Search for similar documents."""
        body = {
            "vector": query_embedding,
            "topK": limit,
            "includeMetadata": True,
            "namespace": "default"
        }

        if filters:
            body["filter"] = filters

        response = await self.client.post("/query", json=body)
        response.raise_for_status()
        data = response.json()

        documents = []
        for match in data.get("matches", []):
            metadata = match.get("metadata", {})
            content = metadata.pop("content", "")
            documents.append(Document(
                id=match["id"],
                content=content,
                embedding=match.get("values"),
                metadata=metadata,
                score=match["score"]
            ))

        return documents

    async def delete(self, document_ids: List[str]) -> bool:
        """Delete documents by ID."""
        response = await self.client.post(
            "/vectors/delete",
            json={"ids": document_ids, "namespace": "default"}
        )
        return response.status_code == 200

    async def health_check(self) -> bool:
        """Check Pinecone index health."""
        try:
            response = await self.client.get("/describe_index_stats")
            return response.status_code == 200
        except Exception:
            return False


class ChromaDBVectorStore(BaseVectorStore):
    """ChromaDB vector store implementation."""

    def __init__(self, config: VectorStoreConfig):
        super().__init__(config)
        self.base_url = f"http://{config.host}:{config.port}"
        self.collection_name = config.index_name

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0
        )

    async def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        try:
            await self.client.post(
                "/api/v1/collections",
                json={
                    "name": self.collection_name,
                    "metadata": {"hnsw:space": "cosine"}
                }
            )
        except Exception:
            pass  # Collection may already exist

    async def index(self, documents: List[Document]) -> bool:
        """Index documents into ChromaDB."""
        await self._ensure_collection()

        response = await self.client.post(
            f"/api/v1/collections/{self.collection_name}/add",
            json={
                "ids": [doc.id for doc in documents],
                "embeddings": [doc.embedding for doc in documents],
                "documents": [doc.content for doc in documents],
                "metadatas": [doc.metadata for doc in documents]
            }
        )
        return response.status_code == 200

    async def search(self, query_embedding: List[float], limit: int = 5,
                    filters: Optional[Dict] = None) -> List[Document]:
        """Search for similar documents."""
        body = {
            "query_embeddings": [query_embedding],
            "n_results": limit,
            "include": ["documents", "metadatas", "distances"]
        }

        if filters:
            body["where"] = filters

        response = await self.client.post(
            f"/api/v1/collections/{self.collection_name}/query",
            json=body
        )
        response.raise_for_status()
        data = response.json()

        documents = []
        if data.get("ids") and data["ids"][0]:
            for i, doc_id in enumerate(data["ids"][0]):
                documents.append(Document(
                    id=doc_id,
                    content=data["documents"][0][i] if data.get("documents") else "",
                    metadata=data["metadatas"][0][i] if data.get("metadatas") else {},
                    score=1.0 - data["distances"][0][i] if data.get("distances") else 0.0
                ))

        return documents

    async def delete(self, document_ids: List[str]) -> bool:
        """Delete documents by ID."""
        response = await self.client.post(
            f"/api/v1/collections/{self.collection_name}/delete",
            json={"ids": document_ids}
        )
        return response.status_code == 200

    async def health_check(self) -> bool:
        """Check ChromaDB health."""
        try:
            response = await self.client.get("/api/v1/heartbeat")
            return response.status_code == 200
        except Exception:
            return False


class InMemoryVectorStore(BaseVectorStore):
    """In-memory vector store for development and testing."""

    def __init__(self, config: VectorStoreConfig):
        super().__init__(config)
        self.documents: Dict[str, Document] = {}

        # Pre-populate with sample data
        self._add_sample_data()

    def _add_sample_data(self):
        """Add sample portfolio project data."""
        samples = [
            Document(
                id="doc-1",
                content="AWS Infrastructure Automation: Multi-account Terraform modules with "
                        "Landing Zone patterns, CDK constructs, and Pulumi components for "
                        "enterprise-scale cloud infrastructure management.",
                metadata={"source": "project-1", "category": "infrastructure"}
            ),
            Document(
                id="doc-2",
                content="Kubernetes CI/CD Pipeline: GitOps workflow using ArgoCD with "
                        "progressive delivery, canary deployments, and automated rollbacks "
                        "for cloud-native applications.",
                metadata={"source": "project-3", "category": "devops"}
            ),
            Document(
                id="doc-3",
                content="Real-time Data Streaming: Apache Kafka with Flink for stateful "
                        "stream processing, event sourcing, and CQRS patterns with "
                        "exactly-once semantics.",
                metadata={"source": "project-5", "category": "data"}
            ),
            Document(
                id="doc-4",
                content="MLOps Platform: End-to-end machine learning pipelines with "
                        "feature stores, model registry, A/B testing, and automated "
                        "retraining workflows.",
                metadata={"source": "project-6", "category": "ml"}
            ),
            Document(
                id="doc-5",
                content="Service Mesh Implementation: Multi-cloud Istio deployment with "
                        "mTLS, traffic management, and observability across AWS EKS "
                        "and GCP GKE clusters.",
                metadata={"source": "project-17", "category": "networking"}
            )
        ]

        for doc in samples:
            # Generate simple mock embedding
            import hashlib
            hash_bytes = hashlib.sha256(doc.content.encode()).digest()
            doc.embedding = [(b - 128) / 128.0 for b in hash_bytes] * 48  # 1536 dims
            doc.score = 0.9
            self.documents[doc.id] = doc

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        return dot_product / (norm_a * norm_b) if norm_a and norm_b else 0.0

    async def index(self, documents: List[Document]) -> bool:
        """Index documents into memory."""
        for doc in documents:
            self.documents[doc.id] = doc
        return True

    async def search(self, query_embedding: List[float], limit: int = 5,
                    filters: Optional[Dict] = None) -> List[Document]:
        """Search for similar documents."""
        results = []

        for doc in self.documents.values():
            if filters:
                # Apply metadata filters
                match = all(doc.metadata.get(k) == v for k, v in filters.items())
                if not match:
                    continue

            if doc.embedding:
                score = self._cosine_similarity(query_embedding, doc.embedding)
            else:
                score = 0.5  # Default score for docs without embeddings

            doc_copy = Document(
                id=doc.id,
                content=doc.content,
                embedding=doc.embedding,
                metadata=doc.metadata,
                score=score
            )
            results.append(doc_copy)

        # Sort by score descending
        results.sort(key=lambda d: d.score, reverse=True)
        return results[:limit]

    async def delete(self, document_ids: List[str]) -> bool:
        """Delete documents by ID."""
        for doc_id in document_ids:
            self.documents.pop(doc_id, None)
        return True

    async def health_check(self) -> bool:
        """Always healthy."""
        return True


def create_vector_store(config: VectorStoreConfig) -> BaseVectorStore:
    """Factory function to create vector store based on config."""
    stores = {
        VectorStoreProvider.OPENSEARCH: OpenSearchVectorStore,
        VectorStoreProvider.PINECONE: PineconeVectorStore,
        VectorStoreProvider.CHROMADB: ChromaDBVectorStore,
        VectorStoreProvider.MEMORY: InMemoryVectorStore
    }

    store_class = stores.get(config.provider, InMemoryVectorStore)
    logger.info(f"Creating vector store: {config.provider.value}")
    return store_class(config)
