#!/usr/bin/env python3
"""
Autonomous DevOps Platform - Main Entry Point

Production-grade autonomous remediation platform that automatically
detects, diagnoses, and remediates infrastructure and application issues.

Features:
- Event-driven remediation engine
- Kubernetes and AWS integration
- Runbook-based workflow execution
- Audit logging and compliance tracking
- API server for external integration
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from event_receiver import EventReceiver
from runbook_engine import RunbookEngine
from api_server import create_app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('autonomous-devops')


async def main():
    """Main entry point for the Autonomous DevOps Platform."""
    logger.info("Starting Autonomous DevOps Platform")

    # Initialize components
    runbook_engine = RunbookEngine()
    event_receiver = EventReceiver(runbook_engine)

    # Load runbooks from directory
    runbooks_dir = Path(__file__).parent.parent / "runbooks"
    if runbooks_dir.exists():
        for runbook_file in runbooks_dir.glob("*.yaml"):
            try:
                runbook_engine.load_runbook(runbook_file)
                logger.info(f"Loaded runbook: {runbook_file.name}")
            except Exception as e:
                logger.error(f"Failed to load runbook {runbook_file}: {e}")

    # Create API server
    app = create_app(runbook_engine, event_receiver)

    # Start event receiver
    await event_receiver.start()

    logger.info("Autonomous DevOps Platform is ready")
    logger.info("API Server: http://0.0.0.0:8080")
    logger.info("Webhook Endpoint: http://0.0.0.0:8080/webhook")

    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await event_receiver.stop()


if __name__ == "__main__":
    asyncio.run(main())
