"""Background asyncio event loop runner used by Celery tasks.

Starts a dedicated event loop in a background thread and exposes a
`run_coroutine` helper that submits coroutines to that loop and waits for
their result. This avoids creating/closing event loops per task and
prevents libraries (motor, asyncpg) from being bound to short-lived loops.
"""

from __future__ import annotations

import asyncio
import threading
from typing import Any, Optional

_LOOP: Optional[asyncio.AbstractEventLoop] = None
_THREAD: Optional[threading.Thread] = None


def _start_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()


def ensure_background_loop() -> asyncio.AbstractEventLoop:
    global _LOOP, _THREAD
    if _LOOP is None:
        loop = asyncio.new_event_loop()
        t = threading.Thread(target=_start_loop, args=(loop,), daemon=True)
        t.start()
        _LOOP = loop
        _THREAD = t
    return _LOOP


def run_coroutine(coro: asyncio.coroutine, timeout: Optional[float] = None) -> Any:
    """Submit coroutine to background loop and wait for result.

    Args:
        coro: Coroutine to run in background loop.
        timeout: Optional timeout in seconds for the result.

    Returns:
        The coroutine result or raises its exception.
    """
    loop = ensure_background_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result(timeout=timeout)


__all__ = ['ensure_background_loop', 'run_coroutine']
