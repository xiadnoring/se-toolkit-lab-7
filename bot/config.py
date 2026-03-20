"""Configuration loader — reads secrets from .env.bot.secret."""

from pathlib import Path

from dotenv import load_dotenv


def load_config() -> dict[str, str]:
    """Load configuration from .env.bot.secret.

    Returns:
        Dictionary with configuration values.
    """
    # Find .env.bot.secret in the bot directory
    bot_dir = Path(__file__).parent
    env_file = bot_dir / ".env.bot.secret"

    if not env_file.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {env_file}\n"
            "Copy .env.bot.example to .env.bot.secret and fill in the values."
        )

    # Load environment variables from file
    load_dotenv(env_file)

    import os

    return {
        "BOT_TOKEN": os.getenv("BOT_TOKEN", ""),
        "LMS_API_URL": os.getenv("LMS_API_URL", ""),
        "LMS_API_KEY": os.getenv("LMS_API_KEY", ""),
        "LLM_API_KEY": os.getenv("LLM_API_KEY", ""),
        "LLM_API_BASE_URL": os.getenv("LLM_API_BASE_URL", ""),
        "LLM_API_MODEL": os.getenv("LLM_API_MODEL", ""),
    }
