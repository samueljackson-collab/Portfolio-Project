#!/usr/bin/env python3
"""
LLM Provider Implementations

Supports multiple LLM backends with a unified interface:
- OpenAI (GPT-4, GPT-3.5)
- Azure OpenAI
- Anthropic Claude
- Local models (Ollama)
- Mock provider for testing
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional
import httpx

from config import LLMConfig, LLMProvider

logger = logging.getLogger("llm-provider")


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a complete response."""
        pass

    @abstractmethod
    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream response tokens."""
        pass

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = config.api_base or "https://api.openai.com/v1"
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=config.timeout_seconds
        )

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a complete response."""
        messages = kwargs.get("messages", [{"role": "user", "content": prompt}])

        response = await self.client.post(
            "/chat/completions",
            json={
                "model": self.config.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream response tokens."""
        messages = kwargs.get("messages", [{"role": "user", "content": prompt}])

        async with self.client.stream(
            "POST",
            "/chat/completions",
            json={
                "model": self.config.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "stream": True
            }
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]
                    except json.JSONDecodeError:
                        continue

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI."""
        response = await self.client.post(
            "/embeddings",
            json={
                "model": "text-embedding-ada-002",
                "input": text
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]


class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI Service provider."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.endpoint = config.api_base
        self.api_version = config.api_version or "2024-02-15-preview"
        self.deployment = config.model

        self.client = httpx.AsyncClient(
            base_url=f"{self.endpoint}/openai/deployments/{self.deployment}",
            headers={"api-key": self.api_key},
            params={"api-version": self.api_version},
            timeout=config.timeout_seconds
        )

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a complete response."""
        messages = kwargs.get("messages", [{"role": "user", "content": prompt}])

        response = await self.client.post(
            "/chat/completions",
            json={
                "messages": messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream response tokens."""
        messages = kwargs.get("messages", [{"role": "user", "content": prompt}])

        async with self.client.stream(
            "POST",
            "/chat/completions",
            json={
                "messages": messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "stream": True
            }
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]
                    except json.JSONDecodeError:
                        continue

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using Azure OpenAI."""
        # Use embedding deployment
        embed_client = httpx.AsyncClient(
            base_url=f"{self.endpoint}/openai/deployments/text-embedding-ada-002",
            headers={"api-key": self.api_key},
            params={"api-version": self.api_version},
            timeout=self.config.timeout_seconds
        )
        async with embed_client:
            response = await embed_client.post(
                "/embeddings",
                json={"input": text}
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.client = httpx.AsyncClient(
            base_url="https://api.anthropic.com/v1",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2024-01-01",
                "content-type": "application/json"
            },
            timeout=config.timeout_seconds
        )

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a complete response."""
        messages = kwargs.get("messages", [{"role": "user", "content": prompt}])

        response = await self.client.post(
            "/messages",
            json={
                "model": self.config.model or "claude-3-sonnet-20240229",
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]

    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream response tokens."""
        messages = kwargs.get("messages", [{"role": "user", "content": prompt}])

        async with self.client.stream(
            "POST",
            "/messages",
            json={
                "model": self.config.model or "claude-3-sonnet-20240229",
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "stream": True
            }
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if data["type"] == "content_block_delta":
                            yield data["delta"]["text"]
                    except (json.JSONDecodeError, KeyError):
                        continue

    async def embed(self, text: str) -> List[float]:
        """Anthropic doesn't provide embeddings - use OpenAI fallback."""
        raise NotImplementedError("Anthropic does not provide embeddings. Use OpenAI or another provider.")


class LocalLLMProvider(BaseLLMProvider):
    """Local LLM provider (Ollama compatible)."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.api_base or "http://localhost:11434"
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=config.timeout_seconds
        )

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a complete response."""
        response = await self.client.post(
            "/api/generate",
            json={
                "model": self.config.model or "llama2",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.config.temperature)
                }
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["response"]

    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream response tokens."""
        async with self.client.stream(
            "POST",
            "/api/generate",
            json={
                "model": self.config.model or "llama2",
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": kwargs.get("temperature", self.config.temperature)
                }
            }
        ) as response:
            async for line in response.aiter_lines():
                try:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                except json.JSONDecodeError:
                    continue

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using local model."""
        response = await self.client.post(
            "/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": text
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["embedding"]


class MockLLMProvider(BaseLLMProvider):
    """Mock provider for testing."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.responses = {
            "default": "This is a mock response from the AI assistant. "
                       "In production, this would be generated by a real LLM."
        }

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a mock response."""
        await asyncio.sleep(0.1)  # Simulate latency
        return self.responses.get("default", "Mock response")

    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream mock response tokens."""
        response = self.responses.get("default", "Mock response")
        words = response.split()
        for word in words:
            await asyncio.sleep(0.02)  # Simulate streaming
            yield word + " "

    async def embed(self, text: str) -> List[float]:
        """Generate mock embeddings."""
        import hashlib
        # Generate deterministic mock embeddings based on text hash
        hash_bytes = hashlib.sha256(text.encode()).digest()
        # Create 1536-dimensional embedding from hash
        embedding = []
        for i in range(1536):
            byte_idx = i % len(hash_bytes)
            embedding.append((hash_bytes[byte_idx] - 128) / 128.0)
        return embedding


def create_llm_provider(config: LLMConfig) -> BaseLLMProvider:
    """Factory function to create LLM provider based on config."""
    providers = {
        LLMProvider.OPENAI: OpenAIProvider,
        LLMProvider.AZURE_OPENAI: AzureOpenAIProvider,
        LLMProvider.ANTHROPIC: AnthropicProvider,
        LLMProvider.LOCAL: LocalLLMProvider,
        LLMProvider.MOCK: MockLLMProvider
    }

    provider_class = providers.get(config.provider, MockLLMProvider)
    logger.info(f"Creating LLM provider: {config.provider.value}")
    return provider_class(config)
