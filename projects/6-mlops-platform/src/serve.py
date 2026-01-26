"""
Model Serving API with FastAPI for MLOps Platform.

Provides REST API for:
- Model predictions
- Health checks
- Metrics export
- A/B testing
- Model versioning
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import mlflow
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MLOps Model Serving API",
    description="Production model serving with MLflow integration",
    version="1.0.0",
)

# Global state
loaded_models = {}
prediction_cache = {}
metrics_counter = {"predictions": 0, "errors": 0, "cache_hits": 0}


class PredictionRequest(BaseModel):
    """Request schema for predictions."""

    features: List[List[float]] = Field(
        ..., description="Feature matrix for prediction"
    )
    model_version: Optional[str] = Field(
        None, description="Model version (default: latest)"
    )


class PredictionResponse(BaseModel):
    """Response schema for predictions."""

    predictions: List[float]
    model_version: str
    model_name: str
    prediction_time_ms: float
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    models_loaded: int
    total_predictions: int
    uptime_seconds: float


class ModelInfo(BaseModel):
    """Model information."""

    name: str
    version: str
    stage: str
    metrics: Dict[str, float]
    loaded_at: str


def load_model(model_name: str, version: Optional[str] = None):
    """Load model from MLflow registry."""
    try:
        client = mlflow.tracking.MlflowClient()
        version_str = version

        if version:
            model_uri = f"models:/{model_name}/{version}"
            model_versions = client.search_model_versions(
                f"name='{model_name}' and version='{version}'"
            )
            if model_versions:
                version_str = model_versions[0].version
        else:
            model_versions = client.get_latest_versions(model_name)
            production_versions = [
                v for v in model_versions if getattr(v, "current_stage", "") == "Production"
            ]
            selected_versions = production_versions or model_versions
            if not selected_versions:
                raise ValueError(f"No versions found for model {model_name}")
            latest = max(selected_versions, key=lambda v: int(v.version))
            version_str = latest.version
            model_uri = f"models:/{model_name}/{version_str}"

        model = mlflow.pyfunc.load_model(model_uri)

        loaded_models[model_name] = {
            "model": model,
            "version": version_str,
            "loaded_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"Loaded model: {model_name} version {version_str}")
        return model, version_str

    except Exception as e:
        logger.error(f"Failed to load model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Load models on startup."""
    logger.info("Starting MLOps Serving API...")

    # Set MLflow tracking URI
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    mlflow.set_tracking_uri(mlflow_uri)

    # Preload default model if specified
    default_model = os.getenv("DEFAULT_MODEL_NAME")
    if default_model:
        try:
            load_model(default_model)
            logger.info(f"Preloaded default model: {default_model}")
        except Exception as e:
            logger.warning(f"Could not preload default model: {e}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    import time

    start_time = float(os.getenv("START_TIME", time.time()))
    uptime = time.time() - start_time

    return HealthResponse(
        status="healthy",
        models_loaded=len(loaded_models),
        total_predictions=metrics_counter["predictions"],
        uptime_seconds=uptime,
    )


@app.get("/models", response_model=List[ModelInfo])
async def list_models():
    """List all loaded models."""
    models_info = []

    for model_name, model_data in loaded_models.items():
        models_info.append(
            ModelInfo(
                name=model_name,
                version=model_data["version"],
                stage="Production",  # Simplified
                metrics={},
                loaded_at=model_data["loaded_at"],
            )
        )

    return models_info


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest, background_tasks: BackgroundTasks):
    """Make predictions using loaded model."""
    import time

    start_time = time.time()

    try:
        # Get model name from env or use default
        model_name = os.getenv("MODEL_NAME", "default-model")

        # Load model if not already loaded
        if model_name not in loaded_models:
            model, version = load_model(model_name, request.model_version)
        else:
            model_data = loaded_models[model_name]
            model = model_data["model"]
            version = model_data["version"]

        # Convert features to DataFrame
        feature_env = os.getenv("MODEL_FEATURE_NAMES")
        if feature_env:
            feature_names = [name.strip() for name in feature_env.split(",") if name.strip()]
        else:
            feature_names = [f"feature_{i:02d}" for i in range(len(request.features[0]))]

        if len(feature_names) != len(request.features[0]):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Feature count mismatch: received "
                    f"{len(request.features[0])} values, expected {len(feature_names)}."
                ),
            )

        df = pd.DataFrame(request.features, columns=feature_names)

        # Make predictions
        predictions = model.predict(df)

        # Convert numpy array to list
        if isinstance(predictions, np.ndarray):
            predictions = predictions.tolist()

        # Track metrics
        metrics_counter["predictions"] += len(predictions)

        prediction_time_ms = (time.time() - start_time) * 1000

        return PredictionResponse(
            predictions=predictions,
            model_version=version,
            model_name=model_name,
            prediction_time_ms=round(prediction_time_ms, 2),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    except HTTPException as exc:
        raise exc
    except Exception as e:
        metrics_counter["errors"] += 1
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch", response_model=PredictionResponse)
async def predict_batch(request: PredictionRequest):
    """Batch prediction endpoint (alias for /predict)."""
    return await predict(request, BackgroundTasks())


@app.get("/metrics")
async def get_metrics():
    """Prometheus-style metrics endpoint."""
    metrics_text = f"""# HELP predictions_total Total number of predictions made
# TYPE predictions_total counter
predictions_total {metrics_counter['predictions']}

# HELP prediction_errors_total Total number of prediction errors
# TYPE prediction_errors_total counter
prediction_errors_total {metrics_counter['errors']}

# HELP models_loaded Number of models currently loaded
# TYPE models_loaded gauge
models_loaded {len(loaded_models)}

# HELP cache_hits_total Total cache hits
# TYPE cache_hits_total counter
cache_hits_total {metrics_counter['cache_hits']}
"""

    return metrics_text


@app.post("/models/{model_name}/load")
async def load_model_endpoint(model_name: str, version: Optional[str] = None):
    """Load a specific model version."""
    model, version_str = load_model(model_name, version)

    return {
        "message": f"Model {model_name} version {version_str} loaded successfully",
        "model_name": model_name,
        "version": version_str,
    }


@app.delete("/models/{model_name}")
async def unload_model(model_name: str):
    """Unload a model from memory."""
    if model_name in loaded_models:
        del loaded_models[model_name]
        logger.info(f"Unloaded model: {model_name}")
        return {"message": f"Model {model_name} unloaded"}
    else:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not loaded")


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "service": "MLOps Model Serving API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "batch_predict": "/predict/batch",
            "models": "/models",
            "metrics": "/metrics",
        },
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
