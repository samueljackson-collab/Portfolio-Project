# AI Research Assistant with Grounding

## Overview
Full-stack web chatbot leveraging retrieval-augmented generation (RAG) with Google Programmable Search grounding to deliver factual responses and citations.

## Architecture
- **Frontend:** Next.js 14 app using streaming React server components.
- **Backend:** FastAPI or Node server orchestrating LLM prompts, grounding results, and conversation storage.
- **Retrieval:** Google Search API + internal knowledge base stored in Pinecone/Weaviate.
- **Model Ops:** Uses OpenAI/Anthropic models with fallback, monitored for latency and cost.

## Features
- Citation requirement for every answer with inline references.
- Conversation history stored per user with encryption at rest.
- Admin dashboard for monitoring usage, flagged responses, and feedback loops.

## Setup
1. `npm install` within `app/` directory.
2. Configure `.env` with API keys (OpenAI, Google Search, Pinecone) retrieved via secrets manager.
3. Run dev server: `npm run dev` (backend) + `npm run dev:ui` (frontend) or combined with Turborepo.
4. Tests: `npm run test` (Jest) and `npm run lint`.
5. Deploy via Vercel or containerized to Kubernetes using provided Helm values.

## Safety & Compliance
- Implements content moderation via OpenAI Moderation API and custom policy rules.
- Redaction pipeline ensures PII removal before indexing.
- Audit logs of prompts/responses stored in secure S3 bucket.

