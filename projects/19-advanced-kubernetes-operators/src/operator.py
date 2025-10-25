"""Portfolio deployment operator using Kopf."""
from __future__ import annotations

import asyncio
import kopf


@kopf.on.create('portfolio.example.com', 'v1alpha1', 'portfoliostacks')
async def create_portfolio(spec, name, namespace, logger, **_):  # type: ignore[override]
    image = spec.get('image')
    version = spec.get('version', 'latest')
    logger.info("Creating portfolio stack", name=name, image=image, version=version)
    await asyncio.sleep(1)
    return {'status': 'created', 'version': version}


@kopf.on.update('portfolio.example.com', 'v1alpha1', 'portfoliostacks')
async def update_portfolio(spec, status, logger, **_):
    desired_version = spec.get('version')
    current_version = status.get('version') if status else None
    if desired_version != current_version:
        logger.info("Rolling upgrade", desired=desired_version, current=current_version)
        await asyncio.sleep(1)
        return {'version': desired_version}


@kopf.timer('portfolio.example.com', 'v1alpha1', 'portfoliostacks', interval=300)
async def health_check(spec, status, logger, **_):
    logger.info("Health check", version=status.get('version'))
