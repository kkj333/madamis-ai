import logging

import discord

from .interface import MadamisSupportProvider

logger = logging.getLogger(__name__)


class MadamisSupportBot(discord.Client):
    def __init__(self, provider: MadamisSupportProvider):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.provider = provider

    async def on_ready(self):
        if self.user:
            logger.info("Discord Bot ログイン成功: %s", self.user.name)

    async def on_message(self, message: discord.Message):
        if not self.user or message.author == self.user:
            return

        is_mentioned = self.user in message.mentions
        is_dm = isinstance(message.channel, discord.DMChannel)

        if not (is_mentioned or is_dm):
            return

        logger.debug("メッセージを受信: %s", message.content)

        text = message.content.replace(f"<@{self.user.id}>", "").strip()
        if not text:
            await message.channel.send("マダミスについて、相談内容を送ってください。")
            return

        user_id = f"discord_user_{message.author.id}"

        try:
            progress_msg = await message.reply(
                "回答を準備しています…（少し時間がかかる場合があります）"
            )

            async with message.channel.typing():
                logger.debug("Provider 経由でリクエスト中 (user_id=%s)", user_id)

                reply_text = await self.provider.interpret(text, user_id)

                logger.debug("応答を受信 (先頭20文字): %s...", reply_text[:20])

                await progress_msg.edit(content=reply_text)
                logger.debug("Discord への返信が完了")

        except Exception:
            logger.exception("Discord Bot 処理中エラー")
            try:
                if "progress_msg" in locals():
                    await progress_msg.edit(
                        content="応答中にエラーが発生しました。時間を置いて再度お試しください。"
                    )
                else:
                    await message.reply(
                        "応答中にエラーが発生しました。時間を置いて再度お試しください。"
                    )
            except Exception:
                logger.exception("エラー通知の送信に失敗")
