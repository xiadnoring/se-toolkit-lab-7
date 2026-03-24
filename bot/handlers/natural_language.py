"""Natural language handler with LLM-powered intent routing.

This handler processes plain text messages using the LLM to decide
which backend tools to call. It also provides inline keyboard buttons
for common queries.
"""

from typing import Any

from config import load_config
from services.api_client import LMSAPIClient
from services.llm_client import LLMClient, IntentRouter

# Global router instance (initialized on first use)
_router: IntentRouter | None = None
_api_client: LMSAPIClient | None = None


def _get_router() -> IntentRouter:
    """Get or create the intent router instance."""
    global _router, _api_client

    if _router is None:
        config = load_config()

        # Create API client
        _api_client = LMSAPIClient(
            base_url=config["LMS_API_URL"],
            api_key=config["LMS_API_KEY"],
        )

        # Create LLM client
        llm_client = LLMClient(
            api_key=config["LLM_API_KEY"],
            base_url=config["LLM_API_BASE_URL"],
            model=config["LLM_API_MODEL"],
        )

        # Create intent router
        _router = IntentRouter(llm_client, _api_client)

    return _router


async def handle_natural_language(message: str) -> str:
    """Handle a natural language message using LLM routing.

    Args:
        message: The user's message text

    Returns:
        Response text from the LLM after tool execution
    """
    router = _get_router()
    return await router.route(message)


def get_inline_keyboard() -> list[list[dict[str, Any]]]:
    """Return inline keyboard buttons for common queries.

    These buttons help users discover what they can ask without typing.
    Each button sends a callback query that triggers the corresponding action.

    Returns:
        List of button rows (each row is a list of button dicts)
    """
    return [
        [
            {"text": "📚 Available Labs", "callback_data": "query_labs"},
            {"text": "📊 Score Distribution", "callback_data": "query_scores"},
        ],
        [
            {"text": "🏆 Top Students", "callback_data": "query_top"},
            {"text": "👥 Group Performance", "callback_data": "query_groups"},
        ],
        [
            {"text": "📈 Pass Rates", "callback_data": "query_pass_rates"},
            {"text": "✅ Completion Rate", "callback_data": "query_completion"},
        ],
        [
            {"text": "👋 Enrolled Students", "callback_data": "query_learners"},
            {"text": "🔄 Sync Data", "callback_data": "query_sync"},
        ],
    ]


def get_quick_query_buttons() -> list[list[dict[str, Any]]]:
    """Return quick query suggestion buttons.

    These are predefined questions users can click to see examples
    of natural language queries.

    Returns:
        List of button rows
    """
    return [
        [
            {"text": "❓ What labs exist?", "callback_data": "text_what_labs"},
        ],
        [
            {"text": "📉 Lowest pass rate?", "callback_data": "text_lowest_pass"},
        ],
        [
            {"text": "🎯 Best group in lab 3?", "callback_data": "text_best_group"},
        ],
    ]


# Map callback data to predefined queries
CALLBACK_QUERIES: dict[str, str] = {
    "query_labs": "what labs are available",
    "query_scores": "show me score distribution for lab 4",
    "query_top": "who are the top 5 students in lab 4",
    "query_groups": "compare groups in lab 3",
    "query_pass_rates": "show pass rates for lab 4",
    "query_completion": "what is the completion rate for lab 4",
    "query_learners": "how many students are enrolled",
    "query_sync": "sync data from autochecker",
    "text_what_labs": "what labs are available",
    "text_lowest_pass": "which lab has the lowest pass rate",
    "text_best_group": "which group is doing best in lab 3",
}


async def handle_callback(callback_data: str) -> str:
    """Handle an inline keyboard callback.

    Args:
        callback_data: The callback data from the button

    Returns:
        Response text for the callback
    """
    # Check if this is a predefined query
    if callback_data in CALLBACK_QUERIES:
        return await handle_natural_language(CALLBACK_QUERIES[callback_data])

    return f"Unknown action: {callback_data}"
