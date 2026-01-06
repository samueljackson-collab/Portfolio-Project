#!/usr/bin/env python3
"""
API Server for Autonomous DevOps Platform

Provides REST API endpoints for:
- Webhook event ingestion
- Runbook management
- Execution history
- Health and status
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from functools import wraps
import asyncio

from aiohttp import web

from event_receiver import Event, EventSeverity, EventSource

logger = logging.getLogger('api-server')


def json_response(data: Any, status: int = 200) -> web.Response:
    """Create a JSON response."""
    return web.json_response(data, status=status)


def error_response(message: str, status: int = 400) -> web.Response:
    """Create an error response."""
    return web.json_response({"error": message}, status=status)


def require_json(func):
    """Decorator to require JSON content type."""
    @wraps(func)
    async def wrapper(request: web.Request) -> web.Response:
        if request.content_type != 'application/json':
            return error_response("Content-Type must be application/json", 415)
        return await func(request)
    return wrapper


class APIServer:
    """REST API server for the autonomous DevOps platform."""

    def __init__(self, runbook_engine, event_receiver):
        self.runbook_engine = runbook_engine
        self.event_receiver = event_receiver
        self.start_time = datetime.utcnow()

    # Health Endpoints
    async def health(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return json_response({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        })

    async def ready(self, request: web.Request) -> web.Response:
        """Readiness check endpoint."""
        return json_response({
            "ready": True,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def status(self, request: web.Request) -> web.Response:
        """Get platform status."""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        return json_response({
            "status": "running",
            "uptime_seconds": uptime,
            "event_stats": self.event_receiver.get_stats(),
            "runbooks_loaded": len(self.runbook_engine.runbooks),
            "active_executions": sum(self.runbook_engine.active_executions.values())
        })

    # Webhook Endpoints
    @require_json
    async def webhook_alertmanager(self, request: web.Request) -> web.Response:
        """Receive Alertmanager webhooks."""
        try:
            payload = await request.json()
            events = self.event_receiver.parse_alertmanager_webhook(payload)

            received = 0
            for event in events:
                if await self.event_receiver.receive_event(event):
                    received += 1

            return json_response({
                "received": received,
                "total": len(events)
            })

        except Exception as e:
            logger.error(f"Alertmanager webhook error: {e}")
            return error_response(str(e), 500)

    @require_json
    async def webhook_kubernetes(self, request: web.Request) -> web.Response:
        """Receive Kubernetes event webhooks."""
        try:
            payload = await request.json()
            event = self.event_receiver.parse_kubernetes_event(payload)

            received = await self.event_receiver.receive_event(event)
            return json_response({
                "received": received,
                "event_id": event.id
            })

        except Exception as e:
            logger.error(f"Kubernetes webhook error: {e}")
            return error_response(str(e), 500)

    @require_json
    async def webhook_cloudwatch(self, request: web.Request) -> web.Response:
        """Receive CloudWatch/EventBridge webhooks."""
        try:
            payload = await request.json()
            event = self.event_receiver.parse_cloudwatch_event(payload)

            received = await self.event_receiver.receive_event(event)
            return json_response({
                "received": received,
                "event_id": event.id
            })

        except Exception as e:
            logger.error(f"CloudWatch webhook error: {e}")
            return error_response(str(e), 500)

    @require_json
    async def webhook_generic(self, request: web.Request) -> web.Response:
        """Receive generic webhooks."""
        try:
            payload = await request.json()

            severity_map = {
                "critical": EventSeverity.CRITICAL,
                "high": EventSeverity.HIGH,
                "medium": EventSeverity.MEDIUM,
                "low": EventSeverity.LOW,
                "info": EventSeverity.INFO
            }

            event = Event(
                id=payload.get("id", f"custom-{int(datetime.utcnow().timestamp())}"),
                event_type=payload.get("event_type", payload.get("type", "custom")),
                source=EventSource.CUSTOM,
                severity=severity_map.get(
                    payload.get("severity", "medium"),
                    EventSeverity.MEDIUM
                ),
                title=payload.get("title", payload.get("summary", "Custom Event")),
                description=payload.get("description", payload.get("message", "")),
                metadata=payload.get("metadata", {}),
                labels=payload.get("labels", {})
            )

            received = await self.event_receiver.receive_event(event)
            return json_response({
                "received": received,
                "event_id": event.id
            })

        except Exception as e:
            logger.error(f"Generic webhook error: {e}")
            return error_response(str(e), 500)

    # Event Endpoints
    async def list_events(self, request: web.Request) -> web.Response:
        """List recent events."""
        limit = int(request.query.get("limit", 100))
        events = self.event_receiver.get_recent_events(limit)
        return json_response({
            "events": events,
            "total": len(events)
        })

    async def get_event_stats(self, request: web.Request) -> web.Response:
        """Get event statistics."""
        return json_response(self.event_receiver.get_stats())

    # Runbook Endpoints
    async def list_runbooks(self, request: web.Request) -> web.Response:
        """List registered runbooks."""
        runbooks = self.runbook_engine.get_runbooks()
        return json_response({
            "runbooks": runbooks,
            "total": len(runbooks)
        })

    async def get_runbook(self, request: web.Request) -> web.Response:
        """Get a specific runbook."""
        name = request.match_info["name"]
        runbook = self.runbook_engine.runbooks.get(name)

        if not runbook:
            return error_response(f"Runbook not found: {name}", 404)

        return json_response({
            "name": runbook.name,
            "description": runbook.description,
            "triggers": runbook.triggers,
            "enabled": runbook.enabled,
            "cooldown_seconds": runbook.cooldown_seconds,
            "max_concurrent": runbook.max_concurrent,
            "steps": [
                {
                    "name": s.name,
                    "type": s.action_type.value,
                    "timeout": s.timeout_seconds,
                    "retry_count": s.retry_count
                }
                for s in runbook.steps
            ]
        })

    @require_json
    async def toggle_runbook(self, request: web.Request) -> web.Response:
        """Enable or disable a runbook."""
        name = request.match_info["name"]
        runbook = self.runbook_engine.runbooks.get(name)

        if not runbook:
            return error_response(f"Runbook not found: {name}", 404)

        payload = await request.json()
        runbook.enabled = payload.get("enabled", not runbook.enabled)

        return json_response({
            "name": runbook.name,
            "enabled": runbook.enabled
        })

    @require_json
    async def trigger_runbook(self, request: web.Request) -> web.Response:
        """Manually trigger a runbook execution."""
        name = request.match_info["name"]
        runbook = self.runbook_engine.runbooks.get(name)

        if not runbook:
            return error_response(f"Runbook not found: {name}", 404)

        payload = await request.json()

        # Create a synthetic event
        event = Event(
            id=f"manual-{int(datetime.utcnow().timestamp())}",
            event_type="manual_trigger",
            source=EventSource.CUSTOM,
            severity=EventSeverity.INFO,
            title=f"Manual trigger: {name}",
            description=payload.get("description", "Manually triggered"),
            metadata=payload.get("metadata", {}),
            labels=payload.get("labels", {})
        )

        # Execute runbook
        record = await self.runbook_engine.execute(runbook, event)

        return json_response({
            "execution_id": record.id,
            "status": record.status.value,
            "started_at": record.started_at.isoformat()
        })

    # Execution Endpoints
    async def list_executions(self, request: web.Request) -> web.Response:
        """List runbook executions."""
        runbook_name = request.query.get("runbook")
        limit = int(request.query.get("limit", 100))

        executions = self.runbook_engine.get_executions(runbook_name, limit)

        return json_response({
            "executions": [
                {
                    "id": e.id,
                    "runbook": e.runbook_name,
                    "event_id": e.event_id,
                    "status": e.status.value,
                    "started_at": e.started_at.isoformat(),
                    "completed_at": e.completed_at.isoformat() if e.completed_at else None,
                    "steps_completed": e.steps_completed,
                    "steps_failed": e.steps_failed,
                    "error": e.error
                }
                for e in executions
            ],
            "total": len(executions)
        })

    async def get_execution(self, request: web.Request) -> web.Response:
        """Get a specific execution."""
        execution_id = request.match_info["id"]
        record = self.runbook_engine.get_execution(execution_id)

        if not record:
            return error_response(f"Execution not found: {execution_id}", 404)

        return json_response({
            "id": record.id,
            "runbook": record.runbook_name,
            "event_id": record.event_id,
            "status": record.status.value,
            "started_at": record.started_at.isoformat(),
            "completed_at": record.completed_at.isoformat() if record.completed_at else None,
            "steps_completed": record.steps_completed,
            "steps_failed": record.steps_failed,
            "output": record.output,
            "error": record.error
        })


def create_app(runbook_engine, event_receiver) -> web.Application:
    """Create the aiohttp application."""
    app = web.Application()
    api = APIServer(runbook_engine, event_receiver)

    # Store references
    app['runbook_engine'] = runbook_engine
    app['event_receiver'] = event_receiver
    app['api_server'] = api

    # Health routes
    app.router.add_get('/health', api.health)
    app.router.add_get('/healthz', api.health)
    app.router.add_get('/ready', api.ready)
    app.router.add_get('/readyz', api.ready)
    app.router.add_get('/status', api.status)

    # Webhook routes
    app.router.add_post('/webhook', api.webhook_generic)
    app.router.add_post('/webhook/alertmanager', api.webhook_alertmanager)
    app.router.add_post('/webhook/kubernetes', api.webhook_kubernetes)
    app.router.add_post('/webhook/cloudwatch', api.webhook_cloudwatch)

    # Event routes
    app.router.add_get('/api/v1/events', api.list_events)
    app.router.add_get('/api/v1/events/stats', api.get_event_stats)

    # Runbook routes
    app.router.add_get('/api/v1/runbooks', api.list_runbooks)
    app.router.add_get('/api/v1/runbooks/{name}', api.get_runbook)
    app.router.add_post('/api/v1/runbooks/{name}/toggle', api.toggle_runbook)
    app.router.add_post('/api/v1/runbooks/{name}/trigger', api.trigger_runbook)

    # Execution routes
    app.router.add_get('/api/v1/executions', api.list_executions)
    app.router.add_get('/api/v1/executions/{id}', api.get_execution)

    return app


async def run_server(runbook_engine, event_receiver, host: str = '0.0.0.0',
                    port: int = 8080):
    """Run the API server."""
    app = create_app(runbook_engine, event_receiver)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info(f"API server running on http://{host}:{port}")
    return runner
