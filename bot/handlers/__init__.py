"""Command handlers - pure functions that take input and return text.

These handlers don't know about Telegram. They can be called from:
- --test mode (for offline testing)
- Unit tests
- Telegram bot (when we add integration)
"""

from .commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    HANDLERS,
)

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "HANDLERS",
]
