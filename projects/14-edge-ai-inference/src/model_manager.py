"""Model management for Edge AI Inference Platform."""
from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

import numpy as np

try:
    import onnxruntime as ort
except ImportError:
    ort = None

LOGGER = logging.getLogger(__name__)


class ModelStatus(Enum):
    """Model lifecycle status."""
    DOWNLOADING = "downloading"
    VALIDATING = "validating"
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"
    DEPRECATED = "deprecated"


class ModelFormat(Enum):
    """Supported model formats."""
    ONNX = "onnx"
    TENSORRT = "tensorrt"
    OPENVINO = "openvino"


@dataclass
class ModelMetadata:
    """Metadata for a loaded model."""
    name: str
    version: str
    format: ModelFormat
    input_shape: List[int]
    output_shape: List[int]
    input_dtype: str
    labels: List[str] = field(default_factory=list)
    description: str = ""
    created_at: Optional[datetime] = None
    checksum: Optional[str] = None
    size_bytes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "format": self.format.value,
            "input_shape": self.input_shape,
            "output_shape": self.output_shape,
            "input_dtype": self.input_dtype,
            "labels": self.labels,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "checksum": self.checksum,
            "size_bytes": self.size_bytes,
        }


@dataclass
class LoadedModel:
    """Represents a loaded and ready model."""
    metadata: ModelMetadata
    session: Any  # ONNX InferenceSession
    status: ModelStatus
    load_time_ms: float
    last_inference: Optional[datetime] = None
    inference_count: int = 0
    error_count: int = 0


class ModelCache:
    """LRU cache for loaded models."""

    def __init__(self, max_models: int = 5, max_memory_mb: int = 2048):
        self.max_models = max_models
        self.max_memory_mb = max_memory_mb
        self._cache: Dict[str, LoadedModel] = {}
        self._access_order: List[str] = []
        self._lock = threading.RLock()
        self._total_memory = 0

    def get(self, model_key: str) -> Optional[LoadedModel]:
        """Get a model from cache."""
        with self._lock:
            if model_key in self._cache:
                # Update access order (LRU)
                self._access_order.remove(model_key)
                self._access_order.append(model_key)
                return self._cache[model_key]
            return None

    def put(self, model_key: str, model: LoadedModel) -> None:
        """Add a model to cache."""
        with self._lock:
            # Evict if necessary
            model_size_mb = model.metadata.size_bytes / (1024 * 1024)

            while (
                len(self._cache) >= self.max_models
                or self._total_memory + model_size_mb > self.max_memory_mb
            ) and self._access_order:
                oldest_key = self._access_order.pop(0)
                if oldest_key in self._cache:
                    evicted = self._cache.pop(oldest_key)
                    self._total_memory -= evicted.metadata.size_bytes / (1024 * 1024)
                    LOGGER.info(f"Evicted model from cache: {oldest_key}")

            self._cache[model_key] = model
            self._access_order.append(model_key)
            self._total_memory += model_size_mb

    def remove(self, model_key: str) -> bool:
        """Remove a model from cache."""
        with self._lock:
            if model_key in self._cache:
                model = self._cache.pop(model_key)
                self._access_order.remove(model_key)
                self._total_memory -= model.metadata.size_bytes / (1024 * 1024)
                return True
            return False

    def clear(self) -> None:
        """Clear all cached models."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
            self._total_memory = 0

    def list_models(self) -> List[str]:
        """List all cached model keys."""
        with self._lock:
            return list(self._cache.keys())

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                "cached_models": len(self._cache),
                "max_models": self.max_models,
                "memory_used_mb": self._total_memory,
                "max_memory_mb": self.max_memory_mb,
            }


class ModelManager:
    """Manages model lifecycle for edge inference."""

    def __init__(
        self,
        models_dir: str = "/app/models",
        cache_max_models: int = 5,
        cache_max_memory_mb: int = 2048,
    ):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.cache = ModelCache(cache_max_models, cache_max_memory_mb)
        self._model_registry: Dict[str, ModelMetadata] = {}
        self._download_callbacks: List[Callable] = []
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._lock = threading.RLock()

        # Scan existing models
        self._scan_models()

    def _scan_models(self) -> None:
        """Scan models directory for existing models."""
        for model_path in self.models_dir.glob("*.onnx"):
            try:
                metadata = self._extract_metadata(model_path)
                key = f"{metadata.name}:{metadata.version}"
                self._model_registry[key] = metadata
                LOGGER.info(f"Discovered model: {key}")
            except Exception as e:
                LOGGER.warning(f"Failed to scan model {model_path}: {e}")

    def _extract_metadata(self, model_path: Path) -> ModelMetadata:
        """Extract metadata from a model file."""
        if ort is None:
            raise RuntimeError("ONNX Runtime not installed")

        # Get file info
        stat = model_path.stat()
        checksum = self._compute_checksum(model_path)

        # Load model to extract shapes
        session = ort.InferenceSession(
            str(model_path),
            providers=["CPUExecutionProvider"],
        )

        input_info = session.get_inputs()[0]
        output_info = session.get_outputs()[0]

        # Parse name and version from filename
        stem = model_path.stem
        if "_v" in stem:
            name, version = stem.rsplit("_v", 1)
        else:
            name = stem
            version = "1.0"

        # Load labels if available
        labels = []
        labels_path = model_path.with_suffix(".labels")
        if labels_path.exists():
            labels = labels_path.read_text().strip().split("\n")

        return ModelMetadata(
            name=name,
            version=version,
            format=ModelFormat.ONNX,
            input_shape=list(input_info.shape),
            output_shape=list(output_info.shape),
            input_dtype=input_info.type,
            labels=labels,
            checksum=checksum,
            size_bytes=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_mtime),
        )

    def _compute_checksum(self, path: Path) -> str:
        """Compute SHA256 checksum of a file."""
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def load_model(
        self,
        name: str,
        version: str = "latest",
        force_reload: bool = False,
    ) -> LoadedModel:
        """Load a model for inference."""
        if ort is None:
            raise RuntimeError("ONNX Runtime not installed")

        # Resolve version
        if version == "latest":
            version = self._get_latest_version(name)

        model_key = f"{name}:{version}"

        # Check cache
        if not force_reload:
            cached = self.cache.get(model_key)
            if cached and cached.status == ModelStatus.READY:
                return cached

        # Find model file
        model_path = self._find_model_path(name, version)
        if not model_path:
            raise FileNotFoundError(f"Model not found: {model_key}")

        LOGGER.info(f"Loading model: {model_key}")
        start_time = time.time()

        try:
            # Create ONNX session with optimized providers
            providers = self._get_execution_providers()
            session = ort.InferenceSession(str(model_path), providers=providers)

            metadata = self._model_registry.get(model_key)
            if not metadata:
                metadata = self._extract_metadata(model_path)
                self._model_registry[model_key] = metadata

            load_time = (time.time() - start_time) * 1000

            loaded_model = LoadedModel(
                metadata=metadata,
                session=session,
                status=ModelStatus.READY,
                load_time_ms=load_time,
            )

            self.cache.put(model_key, loaded_model)

            LOGGER.info(f"Model loaded: {model_key} in {load_time:.2f}ms")
            return loaded_model

        except Exception as e:
            LOGGER.error(f"Failed to load model {model_key}: {e}")
            raise

    def _get_execution_providers(self) -> List[str]:
        """Get available execution providers in priority order."""
        available = ort.get_available_providers() if ort else []
        preferred = [
            "TensorrtExecutionProvider",
            "CUDAExecutionProvider",
            "OpenVINOExecutionProvider",
            "CPUExecutionProvider",
        ]
        return [p for p in preferred if p in available]

    def _find_model_path(self, name: str, version: str) -> Optional[Path]:
        """Find model file path."""
        patterns = [
            f"{name}_v{version}.onnx",
            f"{name}-{version}.onnx",
            f"{name}.onnx",
        ]

        for pattern in patterns:
            path = self.models_dir / pattern
            if path.exists():
                return path

        return None

    def _get_latest_version(self, name: str) -> str:
        """Get latest version of a model."""
        versions = []
        for key in self._model_registry:
            if key.startswith(f"{name}:"):
                version = key.split(":")[1]
                versions.append(version)

        if not versions:
            return "1.0"

        # Simple version comparison
        return sorted(versions, reverse=True)[0]

    def unload_model(self, name: str, version: str = "latest") -> bool:
        """Unload a model from cache."""
        if version == "latest":
            version = self._get_latest_version(name)

        model_key = f"{name}:{version}"
        return self.cache.remove(model_key)

    def list_models(self) -> List[Dict[str, Any]]:
        """List all registered models."""
        models = []
        for key, metadata in self._model_registry.items():
            cached = self.cache.get(key)
            models.append({
                "key": key,
                "name": metadata.name,
                "version": metadata.version,
                "format": metadata.format.value,
                "size_bytes": metadata.size_bytes,
                "loaded": cached is not None,
                "status": cached.status.value if cached else "not_loaded",
            })
        return models

    def get_model_info(self, name: str, version: str = "latest") -> Optional[Dict[str, Any]]:
        """Get detailed model information."""
        if version == "latest":
            version = self._get_latest_version(name)

        model_key = f"{name}:{version}"
        metadata = self._model_registry.get(model_key)

        if not metadata:
            return None

        cached = self.cache.get(model_key)

        return {
            **metadata.to_dict(),
            "loaded": cached is not None,
            "status": cached.status.value if cached else "not_loaded",
            "inference_count": cached.inference_count if cached else 0,
            "last_inference": cached.last_inference.isoformat() if cached and cached.last_inference else None,
        }

    def download_model(
        self,
        url: str,
        name: str,
        version: str,
        checksum: Optional[str] = None,
        callback: Optional[Callable] = None,
    ) -> None:
        """Download a model from URL (async)."""

        def _download():
            import urllib.request

            dest_path = self.models_dir / f"{name}_v{version}.onnx"
            temp_path = dest_path.with_suffix(".tmp")

            try:
                LOGGER.info(f"Downloading model: {name}:{version} from {url}")

                urllib.request.urlretrieve(url, temp_path)

                # Validate checksum
                if checksum:
                    actual = self._compute_checksum(temp_path)
                    if actual != checksum:
                        raise ValueError(f"Checksum mismatch: expected {checksum}, got {actual}")

                # Move to final location
                shutil.move(temp_path, dest_path)

                # Register model
                metadata = self._extract_metadata(dest_path)
                self._model_registry[f"{name}:{version}"] = metadata

                LOGGER.info(f"Model downloaded: {name}:{version}")

                if callback:
                    callback(True, None)

            except Exception as e:
                LOGGER.error(f"Download failed: {e}")
                if temp_path.exists():
                    temp_path.unlink()
                if callback:
                    callback(False, str(e))

        self._executor.submit(_download)

    def delete_model(self, name: str, version: str) -> bool:
        """Delete a model from disk and cache."""
        model_key = f"{name}:{version}"

        # Remove from cache
        self.cache.remove(model_key)

        # Remove from registry
        if model_key in self._model_registry:
            del self._model_registry[model_key]

        # Delete file
        model_path = self._find_model_path(name, version)
        if model_path and model_path.exists():
            model_path.unlink()
            LOGGER.info(f"Deleted model: {model_key}")
            return True

        return False

    def cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.stats()
