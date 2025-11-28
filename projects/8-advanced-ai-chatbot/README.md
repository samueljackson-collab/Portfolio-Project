# Project 8: Advanced AI Chatbot

## Overview
A Retrieval-Augmented Generation (RAG) chatbot that indexes portfolio assets, executes tool-augmented workflows, and serves responses through a FastAPI service with WebSocket streaming.

## Architecture
- **Context:** Chat and workflow users need low-latency answers grounded in portfolio knowledge with safe tool execution and observability.
- **Decision:** Front a FastAPI gateway with rate limiting and session persistence, enrich prompts with a managed vector store, and orchestrate LLM + toolchain calls while emitting telemetry to an observability plane.
- **Consequences:** Enables grounded, traceable responses and safe automation, but requires careful prompt/tool governance and robust vector index refresh automation.

[Mermaid source](assets/diagrams/architecture.mmd) · Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

## Key Features
- Hybrid search using dense embeddings and metadata filters
- Memory manager that combines short-term chat history with long-term knowledge base
- Tool orchestration for knowledge graph lookups, deployment automation, and analytics queries
- Guardrail middleware for content filtering and rate limiting

## Running Locally
```bash
pip install -r requirements.txt
uvicorn src.chatbot_service:app --reload
```

## Deployment Options
- **Primary:** FastAPI container deployed on AWS ECS/Fargate with managed vector database (OpenSearch, Pinecone).
- **Alternative:** Azure OpenAI integration with Cosmos DB + Functions for event-driven actions.
- **Offline Mode:** Local inference using GPT4All or Llama.cpp via plugin architecture.
