#!/usr/bin/env python3
"""
Advanced AI Chatbot - Production Configuration

Supports multiple LLM providers and vector stores with environment-based configuration.
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    MOCK = "mock"


class VectorStoreProvider(Enum):
    """Supported vector store providers."""
    OPENSEARCH = "opensearch"
    PINECONE = "pinecone"
    CHROMADB = "chromadb"
    MEMORY = "memory"


@dataclass
class LLMConfig:
    """Configuration for LLM provider."""
    provider: LLMProvider = LLMProvider.MOCK
    model: str = "gpt-4"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout_seconds: int = 60

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Create config from environment variables."""
        provider_str = os.getenv("LLM_PROVIDER", "mock").lower()
        provider = LLMProvider(provider_str) if provider_str in [p.value for p in LLMProvider] else LLMProvider.MOCK

        return cls(
            provider=provider,
            model=os.getenv("LLM_MODEL", "gpt-4"),
            api_key=os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY"),
            api_base=os.getenv("LLM_API_BASE") or os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("LLM_API_VERSION", "2024-02-15-preview"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2048")),
            timeout_seconds=int(os.getenv("LLM_TIMEOUT", "60"))
        )


@dataclass
class VectorStoreConfig:
    """Configuration for vector store."""
    provider: VectorStoreProvider = VectorStoreProvider.MEMORY
    host: str = "localhost"
    port: int = 9200
    index_name: str = "chatbot-docs"
    api_key: Optional[str] = None
    embedding_model: str = "text-embedding-ada-002"
    embedding_dimensions: int = 1536
    use_ssl: bool = True
    verify_certs: bool = True

    @classmethod
    def from_env(cls) -> "VectorStoreConfig":
        """Create config from environment variables."""
        provider_str = os.getenv("VECTOR_STORE_PROVIDER", "memory").lower()
        provider = VectorStoreProvider(provider_str) if provider_str in [p.value for p in VectorStoreProvider] else VectorStoreProvider.MEMORY

        return cls(
            provider=provider,
            host=os.getenv("VECTOR_STORE_HOST", "localhost"),
            port=int(os.getenv("VECTOR_STORE_PORT", "9200")),
            index_name=os.getenv("VECTOR_STORE_INDEX", "chatbot-docs"),
            api_key=os.getenv("VECTOR_STORE_API_KEY") or os.getenv("PINECONE_API_KEY"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002"),
            embedding_dimensions=int(os.getenv("EMBEDDING_DIMENSIONS", "1536")),
            use_ssl=os.getenv("VECTOR_STORE_SSL", "true").lower() == "true",
            verify_certs=os.getenv("VECTOR_STORE_VERIFY_CERTS", "true").lower() == "true"
        )


@dataclass
class SecurityConfig:
    """Security configuration."""
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    api_key_header: str = "X-API-Key"
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit_per_minute: int = 60

    @classmethod
    def from_env(cls) -> "SecurityConfig":
        """Create config from environment variables."""
        origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
        return cls(
            jwt_secret=os.getenv("JWT_SECRET", ""),
            jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            jwt_expiry_hours=int(os.getenv("JWT_EXPIRY_HOURS", "24")),
            api_key_header=os.getenv("API_KEY_HEADER", "X-API-Key"),
            allowed_origins=[o.strip() for o in origins],
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        )


@dataclass
class DatabaseConfig:
    """Database configuration for conversation persistence."""
    url: str = "sqlite:///./chatbot.db"
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create config from environment variables."""
        return cls(
            url=os.getenv("DATABASE_URL", "sqlite:///./chatbot.db"),
            pool_size=int(os.getenv("DATABASE_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "10")),
            echo=os.getenv("DATABASE_ECHO", "false").lower() == "true"
        )


@dataclass
class CacheConfig:
    """Cache configuration."""
    enabled: bool = True
    redis_url: str = "redis://localhost:6379/0"
    ttl_seconds: int = 3600
    max_entries: int = 10000

    @classmethod
    def from_env(cls) -> "CacheConfig":
        """Create config from environment variables."""
        return cls(
            enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            ttl_seconds=int(os.getenv("CACHE_TTL", "3600")),
            max_entries=int(os.getenv("CACHE_MAX_ENTRIES", "10000"))
        )


@dataclass
class AppConfig:
    """Main application configuration."""
    app_name: str = "Advanced AI Chatbot"
    environment: str = "development"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    log_level: str = "INFO"

    llm: LLMConfig = field(default_factory=LLMConfig.from_env)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig.from_env)
    security: SecurityConfig = field(default_factory=SecurityConfig.from_env)
    database: DatabaseConfig = field(default_factory=DatabaseConfig.from_env)
    cache: CacheConfig = field(default_factory=CacheConfig.from_env)

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create config from environment variables."""
        return cls(
            app_name=os.getenv("APP_NAME", "Advanced AI Chatbot"),
            environment=os.getenv("ENVIRONMENT", "development"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            workers=int(os.getenv("WORKERS", "4")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            llm=LLMConfig.from_env(),
            vector_store=VectorStoreConfig.from_env(),
            security=SecurityConfig.from_env(),
            database=DatabaseConfig.from_env(),
            cache=CacheConfig.from_env()
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary (excluding secrets)."""
        return {
            "app_name": self.app_name,
            "environment": self.environment,
            "debug": self.debug,
            "llm": {
                "provider": self.llm.provider.value,
                "model": self.llm.model,
                "temperature": self.llm.temperature
            },
            "vector_store": {
                "provider": self.vector_store.provider.value,
                "host": self.vector_store.host,
                "index_name": self.vector_store.index_name
            },
            "cache": {
                "enabled": self.cache.enabled
            }
        }


# Global config instance
config = AppConfig.from_env()
