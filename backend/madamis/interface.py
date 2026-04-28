from abc import ABC, abstractmethod
import hashlib

from google.genai import types


class MadamisSupportProvider(ABC):
    """マダミスサポートの応答を取得するための抽象インターフェース"""

    @abstractmethod
    async def interpret(self, text: str, user_id: str) -> str:
        """ユーザーの相談テキストに対する AI 応答を取得する。

        Args:
            text: ユーザーから送信された相談・質問
            user_id: ユーザー識別用 ID

        Returns:
            AI からの返答メッセージ
        """
        pass


class LocalAdkProvider(MadamisSupportProvider):
    """ローカルプロセス内で直接 ADK を叩く実装（開発・デバッグ用）"""

    def __init__(self, runner, session_service, app_name: str):
        self.runner = runner
        self.session_service = session_service
        self.app_name = app_name

    async def interpret(self, text: str, user_id: str) -> str:
        session = await self._get_or_create_user_session(user_id)

        adk_message = types.Content(
            role="user",
            parts=[types.Part(text=text)],
        )

        reply_text = ""
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=adk_message,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                reply_text = event.content.parts[0].text
                break

        return (
            reply_text
            or "応答を取得できませんでした。少し待ってからもう一度お試しください。"
        )

    async def _get_or_create_user_session(self, user_id: str):
        session_id = _session_id_for_user(user_id)
        session = await self.session_service.get_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id,
        )
        if session:
            return session

        try:
            return await self.session_service.create_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id,
            )
        except Exception:
            session = await self.session_service.get_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id,
            )
            if session:
                return session
            raise


def _session_id_for_user(user_id: str) -> str:
    digest = hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:32]
    return f"user_{digest}"
