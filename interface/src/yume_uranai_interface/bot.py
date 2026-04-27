import discord
from .interface import YumeUranaiProvider

class YumeUranaiBot(discord.Client):
    def __init__(self, provider: YumeUranaiProvider):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.provider = provider

    async def on_ready(self):
        if self.user:
            print(f"Discord Bot ログイン成功: {self.user.name}")

    async def on_message(self, message: discord.Message):
        if not self.user or message.author == self.user:
            return

        is_mentioned = self.user in message.mentions
        is_dm = isinstance(message.channel, discord.DMChannel)

        if not (is_mentioned or is_dm):
            return

        print(f"DEBUG: メッセージを受信しました: {message.content}")

        text = message.content.replace(f'<@{self.user.id}>', '').strip()
        if not text:
            await message.channel.send("夢の内容を教えていただけますか？")
            return

        # DiscordユーザIDをプレフィックス付きで渡す
        user_id = f"discord_user_{message.author.id}"
        
        try:
            # 即時応答を返してタイムアウトや「回線が混み合っている」エラーを防ぐ
            progress_msg = await message.reply("夢の解釈を準備しています...（少し時間がかかる場合があります）")
            
            async with message.channel.typing():
                print(f"DEBUG: Provider経由で解釈をリクエスト中 (user_id: {user_id})")
                
                # ADKではなくProviderを通じて推論層に処理を委譲
                reply_text = await self.provider.interpret(text, user_id)
                
                print(f"DEBUG: 解釈を受信しました: {reply_text[:20]}...")
                
                # 結果を受信したら、プレースホルダーメッセージを編集して上書き
                await progress_msg.edit(content=reply_text)
                print("DEBUG: Discordへの返信が完了しました")

        except Exception as e:
            print(f"Discord Bot Error: {e}")
            try:
                if 'progress_msg' in locals():
                    await progress_msg.edit(content="夢の解釈中にエラーが発生しました。時間を置いて再度お試しください。")
                else:
                    await message.reply("夢の解釈中にエラーが発生しました。時間を置いて再度お試しください。")
            except Exception as inner_e:
                print(f"Failed to send error message: {inner_e}")
