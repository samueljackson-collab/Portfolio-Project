"""
Sample Flask application for Kubernetes CI/CD demonstration.

This application provides a simple REST API with health checks,
metrics endpoints, and database connectivity suitable for Kubernetes deployment.
"""

from flask import Flask, jsonify, request
import os
import socket
import time
from datetime import datetime, timezone
from functools import wraps

app = Flask(__name__)

# Application metadata
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_NAME = "k8s-cicd-demo"
START_TIME = time.time()

# Configuration settings (loaded from environment)
APP_CONFIG = {
    'debug': os.getenv('DEBUG', 'false').lower() == 'true',
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    'database_url': os.getenv('DATABASE_URL', 'sqlite:///app.db'),
    'cache_ttl': int(os.getenv('CACHE_TTL', '300')),
    'max_connections': int(os.getenv('MAX_CONNECTIONS', '10')),
    'enable_metrics': os.getenv('ENABLE_METRICS', 'true').lower() == 'true',
    'cors_origins': os.getenv('CORS_ORIGINS', '*'),
}

# Feature flags
FEATURE_FLAGS = {
    'new_dashboard': os.getenv('FF_NEW_DASHBOARD', 'false').lower() == 'true',
    'beta_api': os.getenv('FF_BETA_API', 'false').lower() == 'true',
    'dark_mode': os.getenv('FF_DARK_MODE', 'true').lower() == 'true',
}

# Request counter for metrics
request_count = 0


@app.route("/health")
def health():
    """Health check endpoint for Kubernetes probes."""
    uptime = time.time() - START_TIME

    return (
        jsonify(
            {
                "status": "healthy",
                "version": APP_VERSION,
                "uptime_seconds": round(uptime, 2),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ),
        200,
    )


@app.route("/ready")
def ready():
    """Readiness probe endpoint."""
    # In a real app, check database connections, cache, etc.
    return jsonify({"ready": True, "version": APP_VERSION}), 200


@app.route("/")
def home():
    """Home endpoint."""
    hostname = socket.gethostname()

    return (
        jsonify(
            {
                "message": "Hello from Kubernetes CI/CD Pipeline!",
                "version": APP_VERSION,
                "hostname": hostname,
                "pod_name": os.getenv("POD_NAME", hostname),
                "namespace": os.getenv("POD_NAMESPACE", "default"),
            }
        ),
        200,
    )


@app.route("/api/info")
def info():
    """Application info endpoint."""
    return (
        jsonify(
            {
                "name": APP_NAME,
                "version": APP_VERSION,
                "environment": os.getenv("ENVIRONMENT", "development"),
                "python_version": os.sys.version,
                "uptime_seconds": round(time.time() - START_TIME, 2),
            }
        ),
        200,
    )


@app.route("/api/echo", methods=["POST"])
def echo():
    """Echo endpoint for testing POST requests."""
    data = request.get_json()

    return (
        jsonify(
            {
                "received": data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "processed_by": socket.gethostname(),
            }
        ),
        200,
    )


@app.route("/metrics")
def metrics():
    """Prometheus-style metrics endpoint."""
    uptime = time.time() - START_TIME

    metrics_text = f"""# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds counter
app_uptime_seconds {uptime}

# HELP app_version Application version info
# TYPE app_version gauge
app_version{{version="{APP_VERSION}"}} 1
"""

    return metrics_text, 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return (
        jsonify(
            {
                "error": "Not Found",
                "message": "The requested resource was not found",
                "status": 404,
            }
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return (
        jsonify(
            {
                "error": "Internal Server Error",
                "message": "An internal server error occurred",
                "status": 500,
            }
        ),
        500,
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    print(f"Starting {APP_NAME} v{APP_VERSION} on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
