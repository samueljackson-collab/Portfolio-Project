"""FastAPI application for RAG chatbot."""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
import jwt

from .retrieval import hybrid_search, rerank
from .generation import generate_response, stream_response
from .auth import verify_token

app = FastAPI(title="P09 RAG Chatbot", version="1.0.0")

class ChatRequest(BaseModel):
    query: str
    stream: bool = False
    top_k: int = 5
    temperature: float = 0.7

class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]
    grounding_score: float
    tokens_used: int

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(verify_token)
):
    """Main chat endpoint with RAG."""
    # Retrieve relevant context
    results = await hybrid_search(request.query, top_k=request.top_k)
    reranked = await rerank(request.query, results)
    
    # Generate response
    if request.stream:
        return StreamingResponse(
            stream_response(request.query, reranked[:3], request.temperature),
            media_type="text/event-stream"
        )
    else:
        answer, metadata = await generate_response(
            request.query,
            reranked[:3],
            request.temperature
        )
        
        return ChatResponse(
            answer=answer,
            sources=[{"text": r["text"], "source": r["metadata"]["source"]} for r in reranked[:3]],
            grounding_score=metadata["grounding_score"],
            tokens_used=metadata["tokens_used"]
        )

@app.get("/health")
async def health():
    return {"status": "healthy"}
