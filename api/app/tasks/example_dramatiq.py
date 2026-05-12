"""Dramatiq actors for example tasks (replacement for Celery examples)."""

from __future__ import annotations

import asyncio
import time

import dramatiq

from app.core.logging import get_logger

logger = get_logger(__name__)


@dramatiq.actor(queue_name='default')
def example_task_async(name: str, seconds: int = 5):
    time.sleep(seconds)
    logger.info(f'Hello {name}, task finished after {seconds} seconds.')
    return f'Hello {name}, task finished after {seconds} seconds.'


@dramatiq.actor(queue_name='default')
async def async_demo_async(name: str, seconds: int = 5):
    await asyncio.sleep(seconds)
    logger.info(f'async_demo: Hello {name}, task finished after {seconds} seconds.')
    return f'Hello {name}, task finished after {seconds} seconds.'
