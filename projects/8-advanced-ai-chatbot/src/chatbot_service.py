"""FastAPI application implementing a retrieval-augmented chatbot."""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import AsyncIterator, Dict, List

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

LOGGER = logging.getLogger("chatbot")
LOGGER.setLevel(logging.INFO)


@dataclass
class RetrievedDocument:
    content: str
    score: float
    metadata: Dict[str, str]


class VectorStore:
    """Simplified in-memory vector store for demonstration purposes."""

    def __init__(self, documents: List[RetrievedDocument]) -> None:
        self._documents = documents

    async def search(self, query: str, limit: int = 4) -> List[RetrievedDocument]:
        LOGGER.info("Searching vector store", extra={"query": query})
        # Demo: return top-N preloaded documents sorted by fake score
        return sorted(self._documents, key=lambda doc: doc.score, reverse=True)[:limit]


class PromptFormatter:
    def build_prompt(self, question: str, docs: List[RetrievedDocument]) -> str:
        context = "\n\n".join(f"Source: {doc.metadata.get('source', 'unknown')}\n{doc.content}" for doc in docs)
        return (
            "You are an enterprise solutions assistant."
            "Use the provided documentation to answer the user's question."
            "If the answer is unknown, say so.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        )


class DummyLLM:
    async def stream_answer(self, prompt: str) -> AsyncIterator[str]:
        for chunk in prompt.split():
            await asyncio.sleep(0.01)
            yield chunk + " "


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, str]]


class ChatbotService:
    def __init__(self, vector_store: VectorStore, llm: DummyLLM) -> None:
        self.vector_store = vector_store
        self.llm = llm
        self.prompt_builder = PromptFormatter()

    async def answer(self, question: str) -> StreamingResponse:
        documents = await self.vector_store.search(question)
        if not documents:
            raise HTTPException(status_code=404, detail="No context found")

        prompt = self.prompt_builder.build_prompt(question, documents)

        async def iterator() -> AsyncIterator[bytes]:
            async for chunk in self.llm.stream_answer(prompt):
                yield chunk.encode("utf-8")

        sources = [doc.metadata for doc in documents]
        headers = {"X-Chatbot-Sources": json.dumps(sources)}
        return StreamingResponse(iterator(), media_type="text/plain", headers=headers)

    async def websocket_answer(self, websocket: WebSocket) -> None:
        await websocket.accept()
        try:
            while True:
                payload = await websocket.receive_text()
                documents = await self.vector_store.search(payload)
                prompt = self.prompt_builder.build_prompt(payload, documents)
                async for chunk in self.llm.stream_answer(prompt):
                    await websocket.send_text(chunk)
        except WebSocketDisconnect:
            LOGGER.info("Client disconnected")


def get_service() -> ChatbotService:
    documents = [
        RetrievedDocument(content="Terraform automation for AWS multi-account setups.", score=0.98, metadata={"source": "project-1"}),
        RetrievedDocument(content="GitOps strategy leveraging ArgoCD and progressive delivery.", score=0.92, metadata={"source": "project-3"}),
        RetrievedDocument(content="Kafka streaming pipeline with Flink stateful aggregations.", score=0.88, metadata={"source": "project-5"}),
    ]
    return ChatbotService(VectorStore(documents), DummyLLM())


app = FastAPI(title="Portfolio Chatbot")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, service: ChatbotService = Depends(get_service)) -> ChatResponse:
    stream = await service.answer(request.question)
    content = b"".join([chunk async for chunk in stream.body_iterator])  # type: ignore[attr-defined]
    sources = json.loads(stream.headers.get("X-Chatbot-Sources", "[]"))
    return ChatResponse(answer=content.decode("utf-8"), sources=sources)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, service: ChatbotService = Depends(get_service)) -> None:
    await service.websocket_answer(websocket)
