# Project 8: Advanced AI Chatbot

## Overview
A Retrieval-Augmented Generation (RAG) chatbot that indexes portfolio assets, executes tool-augmented workflows, and serves responses through a FastAPI service with WebSocket streaming.

## Architecture
```mermaid
sequenceDiagram
  participant U as User
  participant FE as Web App
  participant API as FastAPI Gateway
  participant VS as Vector Store
  participant LLM as Large Language Model
  participant TOOL as Toolchain

  U->>FE: Question
  FE->>API: POST /chat
  API->>VS: Semantic search (top-k)
  VS-->>API: Relevant context chunks
  API->>LLM: Prompt + context + conversation history
  LLM->>TOOL: Structured tool calls (optional)
  TOOL-->>LLM: Tool execution results
  LLM-->>API: Streaming answer tokens
  API-->>FE: Streamed response
```

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

## Testing
```bash
# From repository root
python -m pytest projects/8-advanced-ai-chatbot/tests
```

## Deployment Options
- **Primary:** FastAPI container deployed on AWS ECS/Fargate with managed vector database (OpenSearch, Pinecone).
- **Alternative:** Azure OpenAI integration with Cosmos DB + Functions for event-driven actions.
- **Offline Mode:** Local inference using GPT4All or Llama.cpp via plugin architecture.
