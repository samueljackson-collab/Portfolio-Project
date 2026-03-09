---
title: Developer Setup
description: - Docker + Docker Compose - Node.js 20 (optional for local dev) - Python 3.11 (optional for local dev) - Java 17 + Gradle (optional for local dev) cd services/api-gateway npm install npm start cd ../p
tags: [documentation, portfolio]
path: portfolio/microservices-demo-app/dev-setup
created: 2026-03-08T22:19:13.940497+00:00
updated: 2026-03-08T22:04:38.059902+00:00
---

# Developer Setup

## Prerequisites
- Docker + Docker Compose
- Node.js 20 (optional for local dev)
- Python 3.11 (optional for local dev)
- Java 17 + Gradle (optional for local dev)

## Local development
```bash
# API Gateway
cd services/api-gateway
npm install
npm start

# Product Service
cd ../product-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8082
```
