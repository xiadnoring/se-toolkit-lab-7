"""Command handlers - pure functions that take input and return text.

These handlers are independent of Telegram. They can be called from:
- --test mode (for offline testing)
- Unit tests
- Telegram bot (when we add integration)
- Natural language routing via LLM
"""

from .commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    HANDLERS,
)
from .natural_language import (
    handle_natural_language,
    handle_callback,
    get_inline_keyboard,
    get_quick_query_buttons,
    CALLBACK_QUERIES,
)

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "HANDLERS",
    "handle_natural_language",
    "handle_callback",
    "get_inline_keyboard",
    "get_quick_query_buttons",
    "CALLBACK_QUERIES",
]
