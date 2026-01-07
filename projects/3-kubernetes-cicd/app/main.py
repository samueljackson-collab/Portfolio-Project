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
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
APP_NAME = 'k8s-cicd-demo'
APP_DESCRIPTION = 'Kubernetes CI/CD Demo Application'
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


@app.route('/health')
def health():
    """Health check endpoint for Kubernetes probes."""
    uptime = time.time() - START_TIME

    return jsonify({
        'status': 'healthy',
        'version': APP_VERSION,
        'uptime_seconds': round(uptime, 2),
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 200


@app.route('/ready')
def ready():
    """Readiness probe endpoint."""
    # In a real app, check database connections, cache, etc.
    return jsonify({
        'ready': True,
        'version': APP_VERSION
    }), 200


@app.route('/')
def home():
    """Home endpoint."""
    hostname = socket.gethostname()

    return jsonify({
        'message': 'Hello from Kubernetes CI/CD Pipeline!',
        'version': APP_VERSION,
        'hostname': hostname,
        'pod_name': os.getenv('POD_NAME', hostname),
        'namespace': os.getenv('POD_NAMESPACE', 'default'),
    }), 200


@app.route('/api/info')
def info():
    """Application info endpoint."""
    return jsonify({
        'name': APP_NAME,
        'version': APP_VERSION,
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'python_version': os.sys.version,
        'uptime_seconds': round(time.time() - START_TIME, 2)
    }), 200


@app.route('/api/echo', methods=['POST'])
def echo():
    """Echo endpoint for testing POST requests."""
    data = request.get_json()

    return jsonify({
        'received': data,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'processed_by': socket.gethostname()
    }), 200


# =============================================================================
# API v1 Endpoints
# =============================================================================

@app.route('/api/v1/status')
def api_v1_status():
    """
    Status endpoint returning application state and version info.

    Returns:
        JSON object with status, version, uptime, and system info
    """
    global request_count
    request_count += 1

    uptime = time.time() - START_TIME
    hostname = socket.gethostname()

    return jsonify({
        'status': 'operational',
        'version': APP_VERSION,
        'name': APP_NAME,
        'description': APP_DESCRIPTION,
        'uptime': {
            'seconds': round(uptime, 2),
            'human_readable': _format_uptime(uptime)
        },
        'system': {
            'hostname': hostname,
            'pod_name': os.getenv('POD_NAME', hostname),
            'namespace': os.getenv('POD_NAMESPACE', 'default'),
            'node_name': os.getenv('NODE_NAME', 'unknown'),
            'pod_ip': os.getenv('POD_IP', '0.0.0.0'),
        },
        'build': {
            'commit': os.getenv('GIT_COMMIT', 'unknown'),
            'branch': os.getenv('GIT_BRANCH', 'unknown'),
            'build_date': os.getenv('BUILD_DATE', 'unknown'),
        },
        'request_count': request_count,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 200


@app.route('/api/v1/config')
def api_v1_config():
    """
    Configuration endpoint returning non-sensitive app configuration.

    Returns:
        JSON object with application configuration settings
    """
    # Return sanitized config (no secrets)
    safe_config = {
        'debug': APP_CONFIG['debug'],
        'log_level': APP_CONFIG['log_level'],
        'cache_ttl': APP_CONFIG['cache_ttl'],
        'max_connections': APP_CONFIG['max_connections'],
        'enable_metrics': APP_CONFIG['enable_metrics'],
        'cors_origins': APP_CONFIG['cors_origins'],
        # Database URL is sanitized to hide credentials
        'database_configured': bool(APP_CONFIG['database_url']),
    }

    return jsonify({
        'config': safe_config,
        'feature_flags': FEATURE_FLAGS,
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 200


@app.route('/api/v1/tasks', methods=['GET'])
def api_v1_list_tasks():
    """List all tasks (database demo endpoint)."""
    try:
        from database import get_all_tasks
        tasks = get_all_tasks()
        return jsonify({
            'tasks': tasks,
            'count': len(tasks),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
    except ImportError:
        return jsonify({
            'tasks': [],
            'count': 0,
            'message': 'Database module not configured',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500


@app.route('/api/v1/tasks', methods=['POST'])
def api_v1_create_task():
    """Create a new task (database demo endpoint)."""
    try:
        from database import create_task
        data = request.get_json()

        if not data or 'title' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Title is required'
            }), 400

        task = create_task(
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 'medium')
        )

        return jsonify({
            'task': task,
            'message': 'Task created successfully',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 201
    except ImportError:
        return jsonify({
            'error': 'Database not configured',
            'message': 'Database module not available'
        }), 503
    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500


@app.route('/api/v1/tasks/<int:task_id>', methods=['GET'])
def api_v1_get_task(task_id):
    """Get a specific task by ID."""
    try:
        from database import get_task_by_id
        task = get_task_by_id(task_id)

        if not task:
            return jsonify({
                'error': 'Not Found',
                'message': f'Task {task_id} not found'
            }), 404

        return jsonify({
            'task': task,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
    except ImportError:
        return jsonify({
            'error': 'Database not configured',
            'message': 'Database module not available'
        }), 503
    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500


@app.route('/api/v1/tasks/<int:task_id>', methods=['PUT'])
def api_v1_update_task(task_id):
    """Update an existing task."""
    try:
        from database import update_task
        data = request.get_json()

        task = update_task(task_id, data)

        if not task:
            return jsonify({
                'error': 'Not Found',
                'message': f'Task {task_id} not found'
            }), 404

        return jsonify({
            'task': task,
            'message': 'Task updated successfully',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
    except ImportError:
        return jsonify({
            'error': 'Database not configured',
            'message': 'Database module not available'
        }), 503
    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500


@app.route('/api/v1/tasks/<int:task_id>', methods=['DELETE'])
def api_v1_delete_task(task_id):
    """Delete a task."""
    try:
        from database import delete_task
        success = delete_task(task_id)

        if not success:
            return jsonify({
                'error': 'Not Found',
                'message': f'Task {task_id} not found'
            }), 404

        return jsonify({
            'message': f'Task {task_id} deleted successfully',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
    except ImportError:
        return jsonify({
            'error': 'Database not configured',
            'message': 'Database module not available'
        }), 503
    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500


def _format_uptime(seconds: float) -> str:
    """Format uptime in human-readable format."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")

    return " ".join(parts)


@app.route('/metrics')
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

    return metrics_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'status': 404
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An internal server error occurred',
        'status': 500
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'

    print(f"Starting {APP_NAME} v{APP_VERSION} on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
