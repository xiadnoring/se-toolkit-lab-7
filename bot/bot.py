#!/usr/bin/env python3
"""
Telegram bot entry point with --test mode for offline testing.

Usage:
    uv run bot.py --test "/start"    # Test mode - prints response to stdout
    uv run bot.py                    # Normal mode - connects to Telegram
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add bot directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from config import load_config
from handlers import HANDLERS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def run_test_mode(command: str) -> None:
    """Run a command in test mode - calls handler directly and prints result."""
    # Parse command and arguments
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0]
    args = parts[1] if len(parts) > 1 else ""

    # Find handler
    handler = HANDLERS.get(cmd)
    if not handler:
        print(f"Unknown command: {cmd}")
        print("Available commands: " + ", ".join(HANDLERS.keys()))
        sys.exit(1)

    # Call handler (async) and print result
    response = await handler(args)
    print(response)
    sys.exit(0)


async def run_telegram_mode() -> None:
    """Run the bot in Telegram mode - connects to Telegram API."""
    config = load_config()

    if not config["BOT_TOKEN"]:
        logger.error("BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)

    # Initialize bot and dispatcher
    bot = Bot(token=config["BOT_TOKEN"])
    dp = Dispatcher()

    logger.info("Bot started successfully")

    # Register command handlers
    @dp.message(CommandStart())
    async def handle_start(message: Message) -> None:
        """Handle /start command."""
        response = await HANDLERS["/start"]("")
        await message.answer(response)

    @dp.message(Command("help"))
    async def handle_help(message: Message) -> None:
        """Handle /help command."""
        response = await HANDLERS["/help"]("")
        await message.answer(response)

    @dp.message(Command("health"))
    async def handle_health(message: Message) -> None:
        """Handle /health command."""
        response = await HANDLERS["/health"]("")
        await message.answer(response)

    @dp.message(Command("labs"))
    async def handle_labs(message: Message) -> None:
        """Handle /labs command."""
        response = await HANDLERS["/labs"]("")
        await message.answer(response)

    @dp.message(Command("scores"))
    async def handle_scores(message: Message) -> None:
        """Handle /scores command with optional lab argument."""
        # Extract lab name from command arguments
        lab_name = message.text.split(maxsplit=1)
        lab_arg = lab_name[1] if len(lab_name) > 1 else ""
        response = await HANDLERS["/scores"](lab_arg)
        await message.answer(response)

    # Start polling
    await dp.start_polling(bot)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LMS Telegram Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run bot.py --test "/start"
  uv run bot.py --test "/help"
  uv run bot.py --test "/health"
  uv run bot.py --test "/scores lab-04"
""",
    )
    parser.add_argument(
        "--test",
        metavar="COMMAND",
        help="Run in test mode with the given command",
    )

    args = parser.parse_args()

    if args.test:
        asyncio.run(run_test_mode(args.test))
    else:
        asyncio.run(run_telegram_mode())


if __name__ == "__main__":
    main()
