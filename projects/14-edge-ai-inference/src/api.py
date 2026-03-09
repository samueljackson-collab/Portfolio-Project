"""FastAPI REST API for Edge AI Inference Platform."""
from __future__ import annotations

import base64
import io
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from PIL import Image

from .model_manager import ModelManager, ModelStatus
from .inference_service import preprocess

LOGGER = logging.getLogger(__name__)

# Prometheus metrics
INFERENCE_COUNT = Counter(
    "edge_inference_total",
    "Total inference requests",
    ["model", "status"]
)
INFERENCE_LATENCY = Histogram(
    "edge_inference_latency_seconds",
    "Inference latency in seconds",
    ["model"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)
GPU_MEMORY_USED = Gauge(
    "edge_gpu_memory_used_bytes",
    "GPU memory used in bytes"
)
MODELS_LOADED = Gauge(
    "edge_models_loaded",
    "Number of models currently loaded"
)

# Global instances
model_manager: Optional[ModelManager] = None
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global model_manager

    import os
    models_dir = os.environ.get("MODELS_DIR", "/app/models")
    cache_max_models = int(os.environ.get("CACHE_MAX_MODELS", "5"))
    cache_max_memory = int(os.environ.get("CACHE_MAX_MEMORY_MB", "2048"))

    model_manager = ModelManager(
        models_dir=models_dir,
        cache_max_models=cache_max_models,
        cache_max_memory_mb=cache_max_memory,
    )

    LOGGER.info("Edge AI Inference Platform started")
    yield
    LOGGER.info("Edge AI Inference Platform shutting down")


app = FastAPI(
    title="Edge AI Inference API",
    description="REST API for edge-optimized AI inference",
    version="1.0.0",
    lifespan=lifespan,
)


# Request/Response Models
class InferenceRequest(BaseModel):
    """Inference request model."""
    model_name: str = Field(..., description="Name of the model to use")
    model_version: str = Field(default="latest", description="Model version")
    input_data: Optional[List[List[List[List[float]]]]] = Field(
        None, description="Raw input tensor data"
    )
    input_base64: Optional[str] = Field(
        None, description="Base64-encoded image data"
    )
    preprocess: bool = Field(default=True, description="Apply preprocessing")
    top_k: int = Field(default=5, ge=1, le=100, description="Top-K results to return")


class InferenceResult(BaseModel):
    """Single inference result."""
    class_id: int
    label: Optional[str] = None
    confidence: float


class InferenceResponse(BaseModel):
    """Inference response model."""
    model_name: str
    model_version: str
    results: List[InferenceResult]
    inference_time_ms: float
    preprocessing_time_ms: float = 0.0
    total_time_ms: float


class BatchInferenceRequest(BaseModel):
    """Batch inference request."""
    model_name: str
    model_version: str = "latest"
    inputs: List[str]  # List of base64-encoded images
    top_k: int = 5


class BatchInferenceResponse(BaseModel):
    """Batch inference response."""
    model_name: str
    model_version: str
    results: List[List[InferenceResult]]
    total_images: int
    total_time_ms: float
    avg_time_per_image_ms: float


class ModelInfo(BaseModel):
    """Model information."""
    name: str
    version: str
    format: str
    input_shape: List[Any]
    output_shape: List[Any]
    size_bytes: int
    loaded: bool
    status: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    uptime_seconds: float
    gpu_available: bool
    models_loaded: int
    cache_stats: Dict[str, Any]


# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health status."""
    gpu_available = False
    try:
        import onnxruntime as ort
        gpu_available = "CUDAExecutionProvider" in ort.get_available_providers()
    except ImportError:
        pass

    cache_stats = model_manager.cache_stats() if model_manager else {}
    MODELS_LOADED.set(cache_stats.get("cached_models", 0))

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime_seconds=time.time() - start_time,
        gpu_available=gpu_available,
        models_loaded=cache_stats.get("cached_models", 0),
        cache_stats=cache_stats,
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.post("/infer", response_model=InferenceResponse)
async def run_inference(request: InferenceRequest):
    """Run inference on a single input."""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not initialized")

    total_start = time.time()
    preprocess_time = 0.0

    try:
        # Load model
        loaded_model = model_manager.load_model(request.model_name, request.model_version)

        if loaded_model.status != ModelStatus.READY:
            raise HTTPException(status_code=503, detail=f"Model not ready: {loaded_model.status}")

        # Prepare input
        if request.input_base64:
            preprocess_start = time.time()
            image_data = base64.b64decode(request.input_base64)
            image = Image.open(io.BytesIO(image_data))

            if request.preprocess:
                input_tensor = preprocess_image(image, loaded_model.metadata.input_shape)
            else:
                input_tensor = np.array(image).astype(np.float32)
                input_tensor = np.expand_dims(input_tensor.transpose(2, 0, 1), 0)

            preprocess_time = (time.time() - preprocess_start) * 1000
        elif request.input_data:
            input_tensor = np.array(request.input_data, dtype=np.float32)
        else:
            raise HTTPException(status_code=400, detail="No input data provided")

        # Run inference
        inference_start = time.time()
        input_name = loaded_model.session.get_inputs()[0].name
        outputs = loaded_model.session.run(None, {input_name: input_tensor})
        inference_time = (time.time() - inference_start) * 1000

        # Process results
        logits = outputs[0][0]
        top_indices = np.argsort(logits)[-request.top_k:][::-1]

        results = []
        for idx in top_indices:
            label = None
            if loaded_model.metadata.labels and idx < len(loaded_model.metadata.labels):
                label = loaded_model.metadata.labels[idx]

            results.append(InferenceResult(
                class_id=int(idx),
                label=label,
                confidence=float(softmax(logits)[idx]),
            ))

        # Update metrics
        total_time = (time.time() - total_start) * 1000
        loaded_model.inference_count += 1
        loaded_model.last_inference = datetime.utcnow()

        INFERENCE_COUNT.labels(model=request.model_name, status="success").inc()
        INFERENCE_LATENCY.labels(model=request.model_name).observe(inference_time / 1000)

        return InferenceResponse(
            model_name=request.model_name,
            model_version=loaded_model.metadata.version,
            results=results,
            inference_time_ms=inference_time,
            preprocessing_time_ms=preprocess_time,
            total_time_ms=total_time,
        )

    except FileNotFoundError as e:
        INFERENCE_COUNT.labels(model=request.model_name, status="not_found").inc()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        INFERENCE_COUNT.labels(model=request.model_name, status="error").inc()
        LOGGER.exception(f"Inference failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/infer/image", response_model=InferenceResponse)
async def run_inference_image(
    model_name: str,
    model_version: str = "latest",
    top_k: int = 5,
    file: UploadFile = File(...),
):
    """Run inference on an uploaded image."""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not initialized")

    total_start = time.time()

    try:
        # Load model
        loaded_model = model_manager.load_model(model_name, model_version)

        # Read and preprocess image
        preprocess_start = time.time()
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        input_tensor = preprocess_image(image, loaded_model.metadata.input_shape)
        preprocess_time = (time.time() - preprocess_start) * 1000

        # Run inference
        inference_start = time.time()
        input_name = loaded_model.session.get_inputs()[0].name
        outputs = loaded_model.session.run(None, {input_name: input_tensor})
        inference_time = (time.time() - inference_start) * 1000

        # Process results
        logits = outputs[0][0]
        top_indices = np.argsort(logits)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            label = None
            if loaded_model.metadata.labels and idx < len(loaded_model.metadata.labels):
                label = loaded_model.metadata.labels[idx]

            results.append(InferenceResult(
                class_id=int(idx),
                label=label,
                confidence=float(softmax(logits)[idx]),
            ))

        total_time = (time.time() - total_start) * 1000

        INFERENCE_COUNT.labels(model=model_name, status="success").inc()
        INFERENCE_LATENCY.labels(model=model_name).observe(inference_time / 1000)

        return InferenceResponse(
            model_name=model_name,
            model_version=loaded_model.metadata.version,
            results=results,
            inference_time_ms=inference_time,
            preprocessing_time_ms=preprocess_time,
            total_time_ms=total_time,
        )

    except Exception as e:
        INFERENCE_COUNT.labels(model=model_name, status="error").inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/infer/batch", response_model=BatchInferenceResponse)
async def run_batch_inference(request: BatchInferenceRequest):
    """Run inference on multiple images."""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not initialized")

    total_start = time.time()

    try:
        loaded_model = model_manager.load_model(request.model_name, request.model_version)
        input_name = loaded_model.session.get_inputs()[0].name

        all_results = []

        for input_b64 in request.inputs:
            image_data = base64.b64decode(input_b64)
            image = Image.open(io.BytesIO(image_data))
            input_tensor = preprocess_image(image, loaded_model.metadata.input_shape)

            outputs = loaded_model.session.run(None, {input_name: input_tensor})
            logits = outputs[0][0]
            top_indices = np.argsort(logits)[-request.top_k:][::-1]

            results = []
            for idx in top_indices:
                label = None
                if loaded_model.metadata.labels and idx < len(loaded_model.metadata.labels):
                    label = loaded_model.metadata.labels[idx]

                results.append(InferenceResult(
                    class_id=int(idx),
                    label=label,
                    confidence=float(softmax(logits)[idx]),
                ))

            all_results.append(results)

        total_time = (time.time() - total_start) * 1000
        avg_time = total_time / len(request.inputs) if request.inputs else 0

        return BatchInferenceResponse(
            model_name=request.model_name,
            model_version=loaded_model.metadata.version,
            results=all_results,
            total_images=len(request.inputs),
            total_time_ms=total_time,
            avg_time_per_image_ms=avg_time,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models", response_model=List[ModelInfo])
async def list_models():
    """List all available models."""
    if not model_manager:
        return []

    models = model_manager.list_models()
    return [
        ModelInfo(
            name=m["name"],
            version=m["version"],
            format=m["format"],
            input_shape=[],
            output_shape=[],
            size_bytes=m["size_bytes"],
            loaded=m["loaded"],
            status=m["status"],
        )
        for m in models
    ]


@app.get("/models/{name}")
async def get_model(name: str, version: str = "latest"):
    """Get model details."""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not initialized")

    info = model_manager.get_model_info(name, version)
    if not info:
        raise HTTPException(status_code=404, detail="Model not found")

    return info


@app.post("/models/{name}/load")
async def load_model(name: str, version: str = "latest"):
    """Load a model into memory."""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not initialized")

    try:
        loaded = model_manager.load_model(name, version)
        return {
            "name": loaded.metadata.name,
            "version": loaded.metadata.version,
            "status": loaded.status.value,
            "load_time_ms": loaded.load_time_ms,
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/models/{name}/unload")
async def unload_model(name: str, version: str = "latest"):
    """Unload a model from memory."""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not initialized")

    success = model_manager.unload_model(name, version)
    return {"success": success}


@app.delete("/models/{name}")
async def delete_model(name: str, version: str):
    """Delete a model from disk."""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not initialized")

    success = model_manager.delete_model(name, version)
    if not success:
        raise HTTPException(status_code=404, detail="Model not found")

    return {"deleted": True}


@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics."""
    if not model_manager:
        return {}
    return model_manager.cache_stats()


def preprocess_image(image: Image.Image, input_shape: List) -> np.ndarray:
    """Preprocess image for inference."""
    # Get target size from input shape (assuming NCHW format)
    if len(input_shape) >= 4:
        height = input_shape[2] if isinstance(input_shape[2], int) else 224
        width = input_shape[3] if isinstance(input_shape[3], int) else 224
    else:
        height, width = 224, 224

    # Resize and convert
    image = image.convert("RGB")
    image = image.resize((width, height))

    # Convert to numpy and normalize
    array = np.array(image).astype("float32") / 255.0

    # Normalize with ImageNet mean/std
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    array = (array - mean) / std

    # Transpose to CHW and add batch dimension
    array = np.transpose(array, (2, 0, 1))
    return np.expand_dims(array, axis=0).astype(np.float32)


def softmax(x: np.ndarray) -> np.ndarray:
    """Compute softmax probabilities."""
    exp_x = np.exp(x - np.max(x))
    return exp_x / exp_x.sum()
