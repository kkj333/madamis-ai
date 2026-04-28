"""madamis-ai - Discord Bot（マダミスサポート、インターフェース層）"""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from .bot import MadamisSupportBot
from .interface import AdkApiProvider
from .logging_config import configure_logging

_interface_root = Path(__file__).resolve().parent.parent
load_dotenv(_interface_root / ".env")
configure_logging()
logger = logging.getLogger(__name__)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

if not DISCORD_BOT_TOKEN:
    logger.error("DISCORD_BOT_TOKEN が設定されていません。")
    sys.exit(1)

logger.info("Discord Bot 起動（マダミスサポート）Backend API: %s", API_BASE_URL)

api_provider = AdkApiProvider(api_base_url=API_BASE_URL)

bot = MadamisSupportBot(provider=api_provider)

if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
