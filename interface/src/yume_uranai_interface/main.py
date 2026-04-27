"""Yume Uranai - Independent Discord Bot (Interface Layer)"""

import os
from dotenv import load_dotenv

from .bot import YumeUranaiBot
from .interface import AdkApiProvider

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

if not DISCORD_BOT_TOKEN:
    print("エラー: DISCORD_BOT_TOKEN が設定されていません。")
    exit(1)

print(f"起動中: Discord Bot (Backend API: {API_BASE_URL})")

# 推論を分離したHTTPプロバイダーを初期化
api_provider = AdkApiProvider(api_base_url=API_BASE_URL)

# インターフェース層のみでBotを構築
bot = YumeUranaiBot(provider=api_provider)

if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
