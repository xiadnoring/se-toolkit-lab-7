"""Command handlers for slash commands.

Handlers are async functions that can be called from:
- Telegram message handlers (async context)
- Test mode (using asyncio.run())
"""

from typing import Any

from config import load_config
from services.api_client import LMSAPIClient

# Global API client instance (initialized on first use)
_api_client: LMSAPIClient | None = None


def _get_api_client() -> LMSAPIClient:
    """Get or create the API client instance."""
    global _api_client
    if _api_client is None:
        config = load_config()
        _api_client = LMSAPIClient(
            base_url=config["LMS_API_URL"],
            api_key=config["LMS_API_KEY"],
        )
    return _api_client


async def handle_start(user_input: str = "") -> str:
    """Handle /start command - returns welcome message."""
    return "Welcome! I'm your LMS assistant bot. Use /help to see available commands."


async def handle_help(user_input: str = "") -> str:
    """Handle /help command - lists available commands."""
    return (
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores <lab> - Get scores for a lab"
    )


async def handle_health(user_input: str = "") -> str:
    """Handle /health command - checks backend status."""
    client = _get_api_client()
    result = await client.health_check()
    if result["status"] == "ok":
        return f"✅ Backend is healthy: {result.get('message', 'OK')}"
    else:
        return f"❌ Backend error: {result.get('message', 'Unknown error')}"


async def handle_labs(user_input: str = "") -> str:
    """Handle /labs command - lists available labs."""
    client = _get_api_client()
    labs = await client.get_labs()
    if not labs:
        return "No labs available. Make sure the backend is synced with data."

    lab_list = "\n".join(f"• {lab['id']}: {lab['name']}" for lab in labs)
    return f"Available labs:\n{lab_list}"


async def handle_scores(user_input: str = "") -> str:
    """Handle /scores command - shows scores for a lab."""
    if not user_input.strip():
        return "Usage: /scores <lab-name>, e.g., /scores lab-04"

    client = _get_api_client()
    result = await client.get_scores(user_input.strip())

    if "error" in result:
        return f"Error: {result['error']}"

    # Format scores data
    lab_id = result.get("lab_id", user_input)
    total = result.get("total_students", 0)
    passed = result.get("passed", 0)
    pass_rate = result.get("pass_rate", 0)
    avg_score = result.get("avg_score", 0)
    groups = result.get("groups", 0)

    return (
        f"Task\n"
        f"📊 Scores for {lab_id}:\n"
        f"👥 Total students: {total}\n"
        f"✅ Passed: {passed}\n"
        f"📈 Pass rate: {pass_rate:.1f}%\n"
        f"🎯 Average score: {avg_score:.1f}\n"
        f"👨‍🎓 Groups: {groups}"
    )


# Map commands to handler functions
HANDLERS: dict[str, Any] = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
    "/scores": handle_scores,
}
