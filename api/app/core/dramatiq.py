"""Dramatiq broker setup for async actors.

Imports this module to configure the Redis broker and set uvloop as
the event loop policy for worker processes.
"""

from __future__ import annotations

import asyncio
import logging
from urllib.parse import urlparse, urlunparse

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware.asyncio import AsyncIO
from dramatiq.results import Results
from dramatiq.results.backends.redis import RedisBackend

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global flag to ensure broker configuration is performed only once
_BROKER_CONFIGURED = False


def _setup_uvloop() -> None:
    """Configure uvloop as the event loop policy if available."""
    try:
        import uvloop
    except ImportError:
        logger.debug('uvloop not installed, using default asyncio event loop')
        return

    try:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        logger.info('Using uvloop for async event loop')
    except Exception as e:
        logger.warning('Failed to set uvloop policy: %s; falling back to default loop', e)


def _build_results_backend_url() -> str | None:
    """
    Build a Redis URL for storing actor results.

    Returns:
        A Redis URL string, or None if results backend should not be used.
    """
    # Prefer explicit configuration if available
    if hasattr(settings, 'dramatiq_results_redis_url') and settings.dramatiq_results_redis_url:
        results_url = settings.dramatiq_results_redis_url
        logger.info('Using explicit results backend URL: %s', results_url)
        return results_url

    # Automatic DB index increment (original_db + 1) - fallback only
    original_url = settings.redis_url
    parsed = urlparse(original_url)

    # Extract current database index
    try:
        # path is like '/0' or '/'
        db_part = parsed.path.lstrip('/')
        if db_part.isdigit():
            current_db = int(db_part)
        else:
            # Fallback to settings.redis_db if available
            current_db = getattr(settings, 'redis_db', 0)
    except (ValueError, AttributeError):
        current_db = 0

    new_db = current_db + 1
    if new_db > 15:
        logger.warning(
            'Cannot auto-increment Redis DB to %d (max 15). '
            'Results middleware will NOT be attached. '
            'Set dramatiq_results_redis_url explicitly.',
            new_db,
        )
        return None

    # Build new URL
    results_path = f'/{new_db}'
    results_url = urlunparse(parsed._replace(path=results_path))
    logger.info(
        'Auto-generated results backend URL (original DB %d → %d): %s',
        current_db,
        new_db,
        results_url,
    )
    return results_url


def configure_dramatiq(force: bool = False) -> None:
    """
    Configure Dramatiq broker, middleware, and event loop policy.

    Args:
        force: If True, reconfigure even if already configured (use sparingly).
    """
    global _BROKER_CONFIGURED
    if _BROKER_CONFIGURED and not force:
        logger.debug('Dramatiq broker already configured, skipping')
        return

    # 1. Event loop policy (uvloop)
    _setup_uvloop()

    # 2. Redis broker
    try:
        broker = RedisBroker(url=settings.redis_url)
        logger.info('Dramatiq Redis broker created: %s', settings.redis_url)
    except Exception as e:
        logger.exception('Failed to create Redis broker: %s', e)
        raise RuntimeError('Cannot start Dramatiq without a Redis broker') from e

    # 3. AsyncIO middleware
    try:
        broker.add_middleware(AsyncIO())
        logger.info('Dramatiq AsyncIO middleware attached')
    except Exception as e:
        logger.exception('Failed to attach AsyncIO middleware: %s', e)
        # AsyncIO middleware is critical for async actors; fail fast if needed
        raise RuntimeError('AsyncIO middleware is required but could not be attached') from e

    # 4. Results middleware (optional)
    results_url = _build_results_backend_url()
    if results_url:
        try:
            result_backend = RedisBackend(url=results_url)
            broker.add_middleware(Results(backend=result_backend))
            logger.info('Dramatiq Results middleware attached with backend: %s', results_url)
        except Exception as e:
            logger.exception('Failed to attach Results middleware: %s', e)
            # Continue without results – not fatal
            logger.warning(
                'Continuing without Results middleware; actor return values will not be stored'
            )
    else:
        logger.info('Results middleware disabled (no valid Redis backend URL)')

    # 5. Set the broker
    dramatiq.set_broker(broker)
    _BROKER_CONFIGURED = True
    logger.info('Dramatiq broker configuration completed successfully')


# Automatically configure when this module is imported
# This allows the worker CLI to just import this module.
configure_dramatiq()

__all__ = ['configure_dramatiq']
