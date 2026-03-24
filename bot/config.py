"""Configuration loader — reads secrets from .env.bot.secret or environment."""

import os
from pathlib import Path

from dotenv import load_dotenv


def load_config() -> dict[str, str]:
    """Load configuration from .env.bot.secret or environment variables.
    
    In Docker, environment variables are set by docker-compose.
    In local development, loads from .env.bot.secret file.
    
    Returns:
        Dictionary with configuration values.
    """
    # Find .env.bot.secret in the bot directory
    bot_dir = Path(__file__).parent
    env_file = bot_dir / ".env.bot.secret"

    # Try to load from file if it exists (local development)
    if env_file.exists():
        load_dotenv(env_file)
    # Otherwise, use environment variables directly (Docker)

    return {
        "BOT_TOKEN": os.getenv("BOT_TOKEN", ""),
        "LMS_API_URL": os.getenv("LMS_API_URL", ""),
        "LMS_API_KEY": os.getenv("LMS_API_KEY", ""),
        "LLM_API_KEY": os.getenv("LLM_API_KEY", ""),
        "LLM_API_BASE_URL": os.getenv("LLM_API_BASE_URL", ""),
        "LLM_API_MODEL": os.getenv("LLM_API_MODEL", ""),
    }
