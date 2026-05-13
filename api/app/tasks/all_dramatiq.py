"""Import all dramatiq actor modules so a single worker can load them.

Start the worker with this module to ensure all actors are registered:

    dramatiq app.tasks.all_dramatiq --processes 1 --threads 8

This file only imports the actor modules; keep it lightweight.
"""

from __future__ import annotations

from app.core import dramatiq  # noqa: F401
from app.tasks import (
    example_dramatiq,  # noqa: F401
    inspection_dramatiq,  # noqa: F401
    ollama_dramatiq,  # noqa: F401
)

__all__: list[str] = []
