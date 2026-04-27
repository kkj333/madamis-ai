from abc import ABC, abstractmethod
from google.genai import types

class YumeUranaiProvider(ABC):
    """夢占いの結果を取得するための抽象インターフェース"""
    
    @abstractmethod
    async def interpret(self, text: str, user_id: str) -> str:
        """夢の解釈を取得する。
        
        Args:
            text (str): ユーザーから送信された夢の内容
            user_id (str): ユーザー識別用ID
            
        Returns:
            str: 夢見師からの返答メッセージ
        """
        pass

class LocalAdkProvider(YumeUranaiProvider):
    """ローカルプロセス内で直接ADKライブラリを叩く実装（開発・デバッグ用）"""
    
    def __init__(self, runner, session_service, app_name: str):
        self.runner = runner
        self.session_service = session_service
        self.app_name = app_name

    async def interpret(self, text: str, user_id: str) -> str:
        # 既存のセッションを探し、なければ作成する
        list_response = await self.session_service.list_sessions(
            app_name=self.app_name,
            user_id=user_id,
        )
        
        if list_response.sessions:
            session = list_response.sessions[0]
        else:
            session = await self.session_service.create_session(
                app_name=self.app_name,
                user_id=user_id,
            )

        adk_message = types.Content(
            role="user",
            parts=[types.Part(text=text)],
        )

        reply_text = ""
        # エージェントからの応答をストリーミングで取得して結合
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=adk_message,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                reply_text = event.content.parts[0].text
                break

        return reply_text or "申し訳ありません、星の導きが途絶えてしまいました。もう一度お試しください。"


