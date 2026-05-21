from abc import ABC, abstractmethod


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
