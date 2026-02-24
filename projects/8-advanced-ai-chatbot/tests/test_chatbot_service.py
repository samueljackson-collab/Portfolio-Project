"""Tests for the advanced AI chatbot service.

Tests core components: VectorStore, PromptFormatter, and ChatbotService
without requiring external LLM APIs.
"""
from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator, List
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.chatbot_service import (
    ChatbotService,
    ChatRequest,
    DummyLLM,
    PromptFormatter,
    RetrievedDocument,
    VectorStore,
    app,
    get_service,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_docs(n: int = 3) -> List[RetrievedDocument]:
    return [
        RetrievedDocument(
            content=f"Document {i} content about topic {i}.",
            score=1.0 - i * 0.1,
            metadata={"source": f"project-{i}"},
        )
        for i in range(n)
    ]


@pytest.fixture
def docs() -> List[RetrievedDocument]:
    return _make_docs(3)


@pytest.fixture
def vector_store(docs) -> VectorStore:
    return VectorStore(docs)


@pytest.fixture
def llm() -> DummyLLM:
    return DummyLLM()


@pytest.fixture
def service(vector_store, llm) -> ChatbotService:
    return ChatbotService(vector_store, llm)


# ---------------------------------------------------------------------------
# RetrievedDocument
# ---------------------------------------------------------------------------

def test_retrieved_document_fields():
    doc = RetrievedDocument(content="hello", score=0.9, metadata={"source": "s1"})
    assert doc.content == "hello"
    assert doc.score == 0.9
    assert doc.metadata["source"] == "s1"


# ---------------------------------------------------------------------------
# VectorStore
# ---------------------------------------------------------------------------

def test_vector_store_search_returns_top_n(vector_store, docs):
    result = asyncio.run(vector_store.search("any query", limit=2))
    assert len(result) == 2
    # Should be sorted by descending score
    assert result[0].score >= result[1].score


def test_vector_store_search_default_limit(vector_store, docs):
    result = asyncio.run(vector_store.search("query"))
    # Default limit is 4, but we only have 3 docs
    assert len(result) <= 4


def test_vector_store_empty():
    store = VectorStore([])
    result = asyncio.run(store.search("query", limit=4))
    assert result == []


# ---------------------------------------------------------------------------
# PromptFormatter
# ---------------------------------------------------------------------------

def test_prompt_formatter_includes_context():
    formatter = PromptFormatter()
    docs = [RetrievedDocument(content="Important info.", score=0.9, metadata={"source": "doc1"})]
    prompt = formatter.build_prompt("What is X?", docs)
    assert "Important info." in prompt
    assert "What is X?" in prompt


def test_prompt_formatter_includes_source():
    formatter = PromptFormatter()
    docs = [RetrievedDocument(content="Content.", score=0.9, metadata={"source": "proj-42"})]
    prompt = formatter.build_prompt("Q?", docs)
    assert "proj-42" in prompt


def test_prompt_formatter_multiple_docs():
    formatter = PromptFormatter()
    docs = _make_docs(3)
    prompt = formatter.build_prompt("question", docs)
    for i in range(3):
        assert f"Document {i}" in prompt


def test_prompt_formatter_empty_docs():
    formatter = PromptFormatter()
    prompt = formatter.build_prompt("question", [])
    assert "question" in prompt
    # context will be empty string but should not crash
    assert isinstance(prompt, str)


# ---------------------------------------------------------------------------
# DummyLLM
# ---------------------------------------------------------------------------

def test_dummy_llm_streams_output():
    llm = DummyLLM()

    async def collect():
        chunks = []
        async for chunk in llm.stream_answer("hello world"):
            chunks.append(chunk)
        return chunks

    chunks = asyncio.run(collect())
    assert len(chunks) >= 2
    combined = "".join(chunks)
    assert "hello" in combined
    assert "world" in combined


# ---------------------------------------------------------------------------
# ChatbotService
# ---------------------------------------------------------------------------

def test_chatbot_service_answer_returns_streaming_response(service):
    from fastapi.responses import StreamingResponse

    async def run():
        return await service.answer("Tell me about Terraform")

    response = asyncio.run(run())
    assert isinstance(response, StreamingResponse)
    assert response.media_type == "text/plain"


def test_chatbot_service_answer_includes_sources(service):
    async def run():
        return await service.answer("question")

    response = asyncio.run(run())
    sources_header = response.headers.get("X-Chatbot-Sources", "[]")
    sources = json.loads(sources_header)
    assert isinstance(sources, list)
    assert len(sources) > 0


def test_chatbot_service_no_documents_raises_404():
    from fastapi import HTTPException

    empty_store = VectorStore([])
    svc = ChatbotService(empty_store, DummyLLM())

    async def run():
        return await svc.answer("question")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(run())
    assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# FastAPI app via TestClient
# ---------------------------------------------------------------------------

client = TestClient(app)


def test_app_chat_endpoint_returns_200():
    response = client.post("/chat", json={"question": "What is Kubernetes?"})
    assert response.status_code == 200


def test_app_chat_endpoint_returns_answer():
    response = client.post("/chat", json={"question": "Explain Kafka"})
    data = response.json()
    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0


def test_app_chat_endpoint_returns_sources():
    response = client.post("/chat", json={"question": "GitOps?"})
    data = response.json()
    assert "sources" in data
    assert isinstance(data["sources"], list)
