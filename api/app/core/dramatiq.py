"""Dramatiq broker setup for async actors.

Imports this module to configure the Redis broker and set uvloop as
the event loop policy for worker processes.
"""

from __future__ import annotations

import asyncio
import logging

try:
    import uvloop
except Exception:  # pragma: no cover - optional dependency
    uvloop = None

import dramatiq
from dramatiq.brokers.redis import RedisBroker

from app.core.config import settings

logger = logging.getLogger(__name__)


def configure_dramatiq() -> None:
    # Prefer uvloop when available for better perf
    if uvloop is not None:
        try:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            logger.info('Using uvloop for async event loop')
        except Exception:
            logger.exception('Failed to set uvloop; falling back to default loop')

    # Configure Redis broker using settings.redis_url
    broker = RedisBroker(url=settings.redis_url)
    dramatiq.set_broker(broker)


# Run configuration on import time so worker CLI can just import this module
configure_dramatiq()

__all__ = ['configure_dramatiq']
